import asyncio

from aio_pika import IncomingMessage, Message, DeliveryMode
from pydantic import ValidationError
from backend.core import get_rabbitmq_setting
from backend.messaging.channel import RabbitMQChannel
from backend.messaging.events import ClickEvent as ClickEventSchema
from backend.messaging.events import QrCodeJobEvent
from backend.messaging.topology import QR_DEAD_KEY, QR_DEAD_LETTER_EXCHANGE
import logging

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 4
CLICK_REQUEUE_DELAY_SECONDS = 1

class ClickConsumer:

    def __init__(self, worker, settings = None):
        self.settings = settings or get_rabbitmq_setting()
        self.worker=worker

    async def handle_message(self, message: IncomingMessage):
        logger.debug("Click event received")
        try:
            event =  ClickEventSchema.model_validate_json(
                message.body
            )
        except ValidationError:
            logger.exception("Invalid click event payload, discarding")
            await message.nack(requeue=False)
            return
        try:
            await self.worker.process_click(event)
            await message.ack()
        except Exception:
            logger.exception("Failed to process click event for url_id=%s", event.url_id)
            await asyncio.sleep(CLICK_REQUEUE_DELAY_SECONDS)
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

    def _attempts(self, message: IncomingMessage) -> int:
        deaths = (message.headers or {}).get("x-death") or []
        return sum(
            int(d.get("count", 0)) for d in deaths
            if d.get("queue") == self.settings.QR_QUEUE and d.get("reason") == "rejected"
        )
    async def _park(self, message: IncomingMessage) -> None:
        channel = await RabbitMQChannel.get_publish_channel()
        dlx = await channel.get_exchange(QR_DEAD_LETTER_EXCHANGE, ensure=False)
        await dlx.publish(
            Message(body=message.body, delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=QR_DEAD_KEY
        )
        await message.ack()
    async def handle_message(self, message: IncomingMessage) -> None:
        try:
            job = QrCodeJobEvent.model_validate_json(message.body)
        except ValidationError:
            logger.exception("Invalid QR job payload, discarding")
            await self._park(message)
            return

        try:
            await self.worker.process_job(job)
        except Exception:
            attempts = self._attempts(message) + 1
            logger.exception("QR job failed for %s (attempt %d)", job.short_code, attempts)
            if attempts >= MAX_ATTEMPTS:
                await self._park(message)
            else:
                await message.reject(requeue=False)
            return
        await message.ack()

        logger.info("QR %s job done for %s", job.action, job.short_code)

    async def consume(self):
        logger.info("Qr Job consumer started...")
        channel = await RabbitMQChannel.get_channel()

        queue = await channel.get_queue(self.settings.QR_QUEUE, ensure=False)

        logger.info(f"Listening on queue: {queue.name}")

        await queue.consume(self.handle_message)

        logger.info("Qr Job Consumer registered")