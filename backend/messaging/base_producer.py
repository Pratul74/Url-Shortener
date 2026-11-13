from backend.core.config import get_rabbitmq_setting
from backend.messaging.channel import RabbitMQChannel
from aio_pika import Message, DeliveryMode
class BaseProducer:
    routing_key: str
    def __init__(self, settings=None):
        self.settings = settings or get_rabbitmq_setting()

    async def _publish(self, body: str, routing_key: str):
        channel = await RabbitMQChannel().get_channel()
        exhange = await channel.get_exchange(
            self.settings.RABBITMQ_EXCHANGE,
            ensure=False
        )
        await exhange.publish(
            Message(
                body=body.encode(),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,

            ),
            routing_key=routing_key,
            mandatory=True,
        )