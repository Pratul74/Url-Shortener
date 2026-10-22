import asyncio

from backend.messaging.topology import RabbitMQTopology
from backend.core import get_rabbitmq_setting
from backend.db.session import AsyncSessionLocal, close_db
from backend.analytics.geoip import GeoIpService
from backend.core.redis import redis_client
from backend.analytics.ua_parser import UserAgentService
from backend.analytics.worker import AnalyticsWorker
from backend.messaging.consumer import ClickConsumer
from backend.analytics.cache import AnalyticsCache
from backend.analytics.flush_worker import AnalyticsFlushWorker

async def main():
    geoip = None
    flush_task = None

    try:
        await RabbitMQTopology.initialize()
        geoip = GeoIpService()
        ua_parser = UserAgentService()
        cache = AnalyticsCache(redis_client)
        worker = AnalyticsWorker(geoip, ua_parser, AsyncSessionLocal, cache)

        consumer = ClickConsumer(worker)

        await consumer.consume()
        flush_task = asyncio.create_task(
            AnalyticsFlushWorker(AsyncSessionLocal).run_forever()
        )
        await asyncio.Future()
    finally:
        if flush_task is not None:
            flush_task.cancel()
        if geoip is not None:
            await geoip.close()
        await close_db()


if __name__ == "__main__":
    setting=get_rabbitmq_setting()
    print(f"Host: {setting.RABBITMQ_HOST!r}")
    print(f"Port: {setting.RABBITMQ_PORT!r}")
    print(f"User: {setting.RABBITMQ_USER!r}")
    asyncio.run(main())
    
