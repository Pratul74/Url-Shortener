import asyncio

from messaging.topology import RabbitMQTopology
from db.session import AsyncSessionLocal, close_db
from .geoip import GeoIpService
from core.redis import redis_client
from .ua_parser import UserAgentService
from .worker import AnalyticsWorker
from repositories import AnalyticsRepository
from messaging.consumer import ClickConsumer
from .cache import AnalyticsCache

async def main():
    session = AsyncSessionLocal()
    geoip = None

    try:
        await RabbitMQTopology.initialize()
        geoip = GeoIpService()
        ua_parser = UserAgentService()
        repo = AnalyticsRepository(session)
        cache = AnalyticsCache(redis_client)

        worker = AnalyticsWorker(geoip, ua_parser, repo, cache)

        consumer = ClickConsumer(worker)

        await consumer.consume()
        await asyncio.Future()
    finally:
        if geoip is not None:
            await geoip.close()
        await session.close()
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
