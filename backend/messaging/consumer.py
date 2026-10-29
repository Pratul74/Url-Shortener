from aio_pika import IncomingMessage
import traceback
from pydantic import ValidationError
from backend.core import get_rabbitmq_setting
from backend.messaging.channel import RabbitMQChannel
from backend.messaging.events import ClickEvent as ClickEventSchema
from backend.messaging.events import QrCodeJobEvent
import logging

logger = logging.getLogger(__name__)

class ClickConsumer:

    def __init__(self, worker, settings = None):
        self.settings = settings or get_rabbitmq_setting()
        self.worker=worker

    async def handle_message(self, message: IncomingMessage):
        logger.info("📨 Message received")
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
        logger.info("Starting analytics consumer...")

        channel = await RabbitMQChannel.get_channel()

        queue = await channel.declare_queue(
            self.settings.ANALYTICS_QUEUE,
            durable=True,
        )

        logger.info(f"Listening on queue: {queue.name}")

        await queue.consume(self.handle_message)

        logger.info("Analytics Consumer registered")

class QrJobConsumer:
    def __init__(self, worker, settings=None):
        self.settings = settings or get_rabbitmq_setting()
        self.worker = worker

    async def handle_message(self, message: IncomingMessage) -> None:
        try:
            job = QrCodeJobEvent.model_validate_json(message.body)
        except ValidationError:
            logger.exception("Invalid QR job payload, discarding")
            await message.reject(requeue=False)
            return

        try:
            await self.worker.process_job(job)
        except Exception:
            logger.exception("QR job failed for %s", job.short_code)
            await message.reject(requeue=False)
            return

        await message.ack()
        logger.info("QR generated for %s", job.short_code)

    async def consume(self):
        logger.info("Qr Job consumer started...")
        channel = await RabbitMQChannel.get_channel()

        queue = await channel.declare_queue(
            self.settings.QR_QUEUE,
            durable=True,
        )

        logger.info(f"Listening on queue: {queue.name}")

        await queue.consume(self.handle_message)

        logger.info("Qr Job Consumer registered")