from backend.core import get_rabbitmq_setting
from aio_pika import Message, DeliveryMode
from backend.messaging.channel import RabbitMQChannel
from backend.messaging.events import ClickEvent as ClickEventSchema

class ClickEventProducer:
    def __init__(self, settings=None):
        self.settings = settings or get_rabbitmq_setting()
    async def publish(self, click_event: ClickEventSchema):
        channel = await RabbitMQChannel.get_channel()

        exchange= await channel.get_exchange(self.settings.RABBITMQ_EXCHANGE)

        message = Message(
            body=click_event.model_dump_json().encode(),
            content_type='application/json',
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        print("Publishing analytics event...")
        await exchange.publish(
            message,
            routing_key=self.settings.RABBITMQ_ROUTING_KEY,
            mandatory=True
        )
        print("Published!")