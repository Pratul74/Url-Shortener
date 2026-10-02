import asyncio
import uuid
from core.redis import redis_client as default_redis_client
from schemas import CreateAnalytics

class AnalyticsCache:

    METRICS = ("country", "city", "browser", "os", "device", "referrer")

    def __init__(self, redis_client=None):
        self.redis_client = redis_client or default_redis_client

    @staticmethod
    def _key(url_id: int):
        return f"analytics:{url_id}"

    @staticmethod
    def _normalize(value: str | None) ->str:
        if value is None:
            return "Unknown"
        return (
            value.strip()
            .lower()
            .replace(" ", "_")
        )


    async def update(self, url_id: int, event: CreateAnalytics):
        key = self._key(url_id)
        pipeline = self.redis_client.pipeline()
        pipeline.hincrby(self._key(url_id), "total_clicks", 1)
        for metric in self.METRICS:
            value = self._normalize(getattr(event, metric))
            pipeline.hincrby(key, f"{metric}:{value}", 1)
        await pipeline.execute()
