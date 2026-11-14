import asyncio

from aio_pika.abc import AbstractChannel
from backend.messaging.rabbitmq import RabbitMQConnection

class RabbitMQChannel:
    _publish_channel: AbstractChannel | None = None
    _publish_lock = asyncio.Lock()

    @staticmethod
    async def get_channel() -> AbstractChannel:
        connection = await RabbitMQConnection.get_connection()
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=10)

        return channel

    @classmethod
    async def get_publish_channel(cls) -> AbstractChannel:
        if cls._publish_channel is None or cls._publish_channel.is_closed:
            async with cls._publish_lock:
                if cls._publish_channel is None or cls._publish_channel.is_closed:
                    connection = await RabbitMQConnection.get_connection()
                    cls._publish_channel = await connection.channel()
        return cls._publish_channel
