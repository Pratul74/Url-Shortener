import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from redis.exceptions import RedisError
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core import get_redis_setting
from backend.core.redis import redis_client
from backend.models.analytics import Analytics
from backend.models.url import Url
from backend.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RedirectTarget:
    id: int
    short_code: str
    original_url: str
    is_active: bool
    expires_at: datetime | None

    @classmethod
    def from_url(cls, url: Url) -> "RedirectTarget":
        return cls(url.id, url.short_code, url.original_url, url.is_active, url.expires_at)


class URLRepository(BaseRepository[Url]):
    def __init__(self, db: AsyncSession, settings=None):
        super().__init__(Url, db)
        self.redis_client = redis_client
        self.settings = settings or get_redis_setting()

    @staticmethod
    def _cache_key(short_code: str) -> str:
        return f"url:{short_code}"

    @staticmethod
    def _aware(dt: datetime | None) -> datetime | None:
        if dt is None:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def _cache_ttl(self, url) -> int:
        ttl = self.settings.REDIS_CACHE_TTL_SECONDS
        exp = self._aware(url.expires_at)
        if exp is None:
            return ttl
        return min(ttl, int((exp - datetime.now(timezone.utc)).total_seconds()))

    @staticmethod
    def _cache_payload(url) -> dict[str, str]:
        return {
            "id": str(url.id),
            "short_code": url.short_code,
            "original_url": url.original_url,
            "is_active": "1" if url.is_active else "0",
            "expires_at": url.expires_at.isoformat() if url.expires_at else "",
        }

    async def _cache_url(self, url) -> None:
        ttl = self._cache_ttl(url)
        if ttl <= 0:
            return
        key = self._cache_key(url.short_code)
        try:
            pipe = self.redis_client.pipeline()
            pipe.hset(key, mapping=self._cache_payload(url))
            pipe.expire(key, ttl)
            await pipe.execute()
        except RedisError:
            logger.exception("Redis SET failed for %s", key)

    async def _delete_cached_url(self, short_code: str) -> None:
        try:
            await self.redis_client.delete(self._cache_key(short_code))
        except RedisError:
            logger.exception("Redis DELETE failed for %s", short_code)

    async def get_for_redirect(self, short_code: str) -> RedirectTarget | None:
        key = self._cache_key(short_code)
        try:
            cached = await self.redis_client.hgetall(key)
        except RedisError:
            logger.exception("Redis unavailable, falling back to DB")
            cached = None

        if cached:
            try:
                return RedirectTarget(
                    id=int(cached["id"]),
                    short_code=cached["short_code"],
                    original_url=cached["original_url"],
                    is_active=cached["is_active"] == "1",
                    expires_at=(
                        datetime.fromisoformat(cached["expires_at"])
                        if cached["expires_at"] else None
                    ),
                )
            except (KeyError, ValueError):
                logger.warning("Corrupt cache entry %s", key)
                await self._delete_cached_url(short_code)

        url = await self.get_by_short_code(short_code)
        if url is None:
            return None
        await self._cache_url(url)
        return RedirectTarget.from_url(url)

    async def get_by_short_code(self, short_code: str) -> Url | None:
        result = await self.db.execute(select(Url).where(Url.short_code == short_code))
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: uuid.UUID, limit: int = 20, offset: int = 0):
        result = await self.db.execute(
            select(Url)
            .where(Url.user_id == user_id)
            .order_by(Url.created_at.desc(), Url.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def create(self, **kwargs) -> Url:
        try:
            url = Url(**kwargs)
            self.db.add(url)
            await self.db.flush()
            self.db.add(Analytics(url_id=url.id))
            await self.db.commit()
            await self.db.refresh(url)
        except Exception:
            logger.exception("Database transaction failed")
            await self.db.rollback()
            raise
        await self._cache_url(url)
        return url

    async def increment_clicks_by_code(self, short_code: str) -> None:
        await self.db.execute(
            update(Url)
            .where(Url.short_code == short_code)
            .values(clicks=Url.clicks + 1, updated_at=func.now())
            .execution_options(synchronize_session=False)
        )
        await self.db.commit()

    async def set_qr_key(self, url: Url, key: str) -> None:
        url.qr_key = key
        await self.db.commit()
        await self.db.refresh(url)

    async def deactivate(self, url: Url) -> None:
        short_code = url.short_code
        url.is_active = False
        await self.db.commit()
        await self._delete_cached_url(short_code)

    async def permanent_delete_url(self, url: Url) -> None:
        short_code = url.short_code
        await self.db.delete(url)
        await self.db.commit()
        await self._delete_cached_url(short_code)
