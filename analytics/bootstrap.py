import asyncio

from messaging.topology import RabbitMQTopology
from core import settings
from db.session import AsyncSessionLocal, close_db
from .geoip import GeoIpService
from core.redis import redis_client
from .ua_parser import UserAgentService
from .worker import AnalyticsWorker
from messaging.consumer import ClickConsumer
from .cache import AnalyticsCache

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
    print(f"Host: {settings.RABBITMQ_HOST!r}")
    print(f"Port: {settings.RABBITMQ_PORT!r}")
    print(f"User: {settings.RABBITMQ_USER!r}")
    asyncio.run(main())
    
