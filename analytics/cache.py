import asyncio
import uuid
from core.redis import redis_client as default_redis_client
from schemas import CreateAnalytics

class AnalyticsCache:

    METRICS = ("country", "city", "browser", "os", "device")

    TTL_SECONDS = 86400

    def __init__(self, redis_client):
        self.redis_client = redis_client or default_redis_client

    @staticmethod
    def _key(url_id: uuid.UUID, metric: str):
        return f"analytics:{url_id}:{metric}"


    async def update(self, url_id: uuid.UUID, event: CreateAnalytics):
        pipeline = self.redis_client.pipeline()
        for metric in self.METRICS:
            value = getattr(event, metric) or "Unknown"
            key = self._key(url_id, metric)
            pipeline.hincrby(key, value, 1)
            pipeline.expire(key, self.TTL_SECONDS)
        await asyncio.to_thread(pipeline.execute)
