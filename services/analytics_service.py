import logging
import uuid

from analytics.parsing import DICT_METRICS, merge_counts, parse_hash
from core.redis import redis_client
from exceptions import UrlNotFoundException
from repositories import AnalyticsRepository
from repositories import URLRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseService

logger = logging.getLogger(__name__)


class AnalyticsService(BaseService):

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.cache = redis_client
        self.analytics_repo = AnalyticsRepository(db)
        self.url_repo = URLRepository(db)

    @staticmethod
    def _key(url_id: int) -> str:
        return f"analytics:{url_id}"

    async def _get_pending(self, url_id: int) -> dict:
        try:
            raw = await self.cache.hgetall(self._key(url_id))
        except Exception:
            logger.exception("Redis unavailable for url_id=%s", url_id)
            raw = {}
        return parse_hash(raw)

    async def get_analytics(self, user_id: uuid.UUID, url_id: int) -> dict:
        url = await self.url_repo.get_by_id(url_id)
        if not url or url.user_id != user_id:
            raise UrlNotFoundException()

        persisted = await self.analytics_repo.get_by_url_id(url_id)
        pending = await self._get_pending(url_id)

        result = {
            "url_id": url_id,
            "total_clicks": (persisted.total_clicks if persisted else 0) + pending["total_clicks"],
        }
        for metric in DICT_METRICS:
            result[metric] = merge_counts(getattr(persisted, metric, None), pending[metric])
        return result

        



    
        