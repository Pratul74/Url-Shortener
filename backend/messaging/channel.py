from aio_pika import Channel
from .rabbitmq import RabbitMQConnection

class RabbitMQChannel:

    @staticmethod
    async def get_channel() -> Channel:
        connection = await RabbitMQConnection.get_connection()
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=10)

        return channel
