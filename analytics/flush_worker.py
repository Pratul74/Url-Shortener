import asyncio
import logging
import time
import uuid

from redis.exceptions import ResponseError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from analytics.parsing import DICT_METRICS, merge_counts, parse_hash
from core.redis import redis_client
from db.session import AsyncSessionLocal
from repositories import AnalyticsRepository

logger = logging.getLogger(__name__)


class AnalyticsFlushWorker:
    LIVE_PATTERN = "analytics:*"
    FLUSH_PREFIX = "flushing:analytics"
    FLUSH_PATTERN = "flushing:analytics:*"

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.cache = redis_client

    async def _claim(self, key: str) -> str | None:
        url_id = key.split(":", 1)[1]
        temp_key = f"{self.FLUSH_PREFIX}:{url_id}:{int(time.time() * 1000)}"
        try:
            await self.cache.rename(key, temp_key)
            return temp_key
        except ResponseError:
            return None 

    async def _merge_analytics(self, url_id: uuid.UUID, data: dict, repo: AnalyticsRepository):
        analytics = await repo.get_by_url_id(url_id=url_id)
        if not analytics:
            logger.warning("No analytics row for url_id=%s; dropping flushed data", url_id)
            return
        analytics.total_clicks = (analytics.total_clicks or 0) + data["total_clicks"]
        for metric in DICT_METRICS:
            setattr(analytics, metric, merge_counts(getattr(analytics, metric), data[metric]))
        await repo.update(analytics)

    async def _process(self, temp_key: str, session: AsyncSession, repo: AnalyticsRepository):
        url_id = uuid.UUID(temp_key.split(":")[2])
        raw = await self.cache.hgetall(temp_key)
        if raw:
            await self._merge_analytics(url_id, parse_hash(raw), repo)
            await session.commit()
        await self.cache.delete(temp_key)

    async def flush(self) -> int:
        flushed = 0
        async with self.session_factory() as session:
            repo = AnalyticsRepository(session)
            temp_keys = [k async for k in self.cache.scan_iter(match=self.FLUSH_PATTERN, count=100)]
            async for key in self.cache.scan_iter(match=self.LIVE_PATTERN, count=100):
                temp_key = await self._claim(key)
                if temp_key:
                    temp_keys.append(temp_key)
            for temp_key in temp_keys:
                try:
                    await self._process(temp_key, session, repo)
                    flushed += 1
                except Exception:
                    await session.rollback()
                    logger.exception("Failed to flush %s (will retry next cycle)", temp_key)
        return flushed

    async def run_forever(self, interval_seconds: int = 120):
        while True:
            try:
                logger.info("Flushed %d urls", await self.flush())
            except Exception:
                logger.exception("Flush cycle failed")
            await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(AnalyticsFlushWorker(AsyncSessionLocal).run_forever())