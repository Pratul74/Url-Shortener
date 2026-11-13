from aio_pika import ExchangeType
from backend.core import get_rabbitmq_setting
from backend.messaging.channel import RabbitMQChannel

QR_RETRY_KEY = "qr.retry"
QR_DEAD_KEY = "qr.dead"
QR_DEAD_LETTER_EXCHANGE = "qr.dlx"

class RabbitMQTopology:

    @staticmethod
    async def initialize():
        settings = get_rabbitmq_setting()
        channel = await RabbitMQChannel.get_channel()

        dlx = await channel.declare_exchange(
            "qr.dlx",
            ExchangeType.DIRECT,
            durable=True,
        )
        
        exchange = await channel.declare_exchange(
            settings.RABBITMQ_EXCHANGE,
            ExchangeType.DIRECT,
            durable=True,
        )

        analytics_queue = await channel.declare_queue(
            settings.ANALYTICS_QUEUE,
            durable=True,
        )

        await analytics_queue.bind(
            exchange, 
            routing_key=settings.ANALYTICS_ROUTING_KEY,
        )

        qr_queue = await channel.declare_queue(
            settings.QR_QUEUE,
            durable=True,
            arguments={
                "x-dead-letter-exchange": dlx.name,
                "x-dead-letter-routing-key": QR_RETRY_KEY
            }
        )
        await qr_queue.bind(
            exchange,
            routing_key=settings.QR_ROUTING_KEY,
        )

        retry_queue = await channel.declare_queue(
            f"{settings.QR_QUEUE}.retry", durable=True,
            arguments={"x-message-ttl": 10_000,
                       "x-dead-letter-exchange": exchange.name,
                       "x-dead-letter-routing-key": settings.QR_ROUTING_KEY},
        )

        await retry_queue.bind(dlx, routing_key=QR_RETRY_KEY)

        dead_queue = await channel.declare_queue(f"{settings.QR_QUEUE}.dead", durable=True)
        await dead_queue.bind(dlx, routing_key=QR_DEAD_KEY)

        return exchange, analytics_queue
