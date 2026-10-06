from core import settings
from aio_pika import Message, DeliveryMode
from .channel import RabbitMQChannel
from .events import ClickEvent as ClickEventSchema

class ClickEventProducer:
    async def publish(self, click_event: ClickEventSchema):
        channel = await RabbitMQChannel.get_channel()

        exchange= await channel.get_exchange(settings.RABBITMQ_EXCHANGE)

        message = Message(
            body=click_event.model_dump_json().encode(),
            content_type='application/json',
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        print("Publishing analytics event...")
        await exchange.publish(
            message,
            routing_key=settings.RABBITMQ_ROUTING_KEY,
            mandatory=True
        )
        print("Published!")