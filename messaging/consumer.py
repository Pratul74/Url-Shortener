from aio_pika import IncomingMessage
from pydantic import ValidationError
from core import settings
from messaging.channel import RabbitMQChannel
from messaging.events import ClickEvent as ClickEventSchema

class ClickConsumer:

    def __init__(self, worker):
        self.worker=worker

    async def handle_message(self, message: IncomingMessage):
        try:
            event =  ClickEventSchema.model_validate_json(
                message.body
            )
        except ValidationError:
            await message.nack(requeue=False)
            return

        try:
            await self.worker.process_click(event)
            await message.ack()
        except Exception:
            await message.nack(requeue=True)

    async def consume(self):
        channel = await RabbitMQChannel.get_channel()

        queue = await channel.get_queue(
            settings.RABBITMQ_QUEUE
        )

        await queue.consume(
            self.handle_message
        )



    