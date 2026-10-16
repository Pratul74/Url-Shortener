from aio_pika import IncomingMessage
import traceback
from pydantic import ValidationError
from core import get_rabbitmq_setting
from messaging.channel import RabbitMQChannel
from messaging.events import ClickEvent as ClickEventSchema

class ClickConsumer:

    def __init__(self, worker, settings = None):
        self.settings = settings or get_rabbitmq_setting()
        self.worker=worker

    async def handle_message(self, message: IncomingMessage):
        print("📨 Message received")
        try:
            event =  ClickEventSchema.model_validate_json(
                message.body
            )
        except ValidationError as e:
            traceback.print_exc()
            await message.nack(requeue=False)
            return
        try:
            await self.worker.process_click(event)
            await message.ack()
        except Exception as e:
            traceback.print_exc()
            await message.nack(requeue=True)

    async def consume(self):
        print("Starting consumer...")

        channel = await RabbitMQChannel.get_channel()

        queue = await channel.declare_queue(
            self.setting.RABBITMQ_QUEUE,
            durable=True,
        )

        print(f"Listening on queue: {queue.name}")

        await queue.consume(self.handle_message)

        print("Consumer registered")