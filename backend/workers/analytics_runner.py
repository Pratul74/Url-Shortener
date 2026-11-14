import asyncio
import logging

from backend.messaging.topology import RabbitMQTopology
from backend.db.session import AsyncSessionLocal, close_db
from backend.analytics.geoip import GeoIpService
from backend.core.redis import redis_client
from backend.analytics.ua_parser import UserAgentService
from backend.workers.analytics_worker import AnalyticsWorker
from backend.messaging.consumer import ClickConsumer
from backend.analytics.cache import AnalyticsCache

async def main():
    geoip = None

    try:
        await RabbitMQTopology.initialize()
        geoip = GeoIpService()
        ua_parser = UserAgentService()
        cache = AnalyticsCache(redis_client)
        worker = AnalyticsWorker(geoip, ua_parser, AsyncSessionLocal, cache)

        consumer = ClickConsumer(worker)

        await consumer.consume()
        await asyncio.Future()
    finally:
        if geoip is not None:
            await geoip.close()
        await close_db()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
