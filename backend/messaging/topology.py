from aio_pika import ExchangeType
from core import settings
from .channel import RabbitMQChannel

class RabbitMQTopology:

    @staticmethod
    async def initialize():
        channel = await RabbitMQChannel.get_channel()
        
        exchange = await channel.declare_exchange(
            settings.RABBITMQ_EXCHANGE,
            ExchangeType.DIRECT,
            durable=True,
        )

        queue = await channel.declare_queue(
            settings.RABBITMQ_QUEUE,
            durable=True,
        )

        await queue.bind(
            exchange, 
            routing_key=settings.RABBITMQ_ROUTING_KEY,
        )

        return exchange, queue