from backend.messaging.base_producer import BaseProducer
from backend.messaging.events import ClickEvent, QrCodeJobEvent
import logging

logger = logging.getLogger(__name__)

class ClickEventProducer(BaseProducer):
    async def publish(self, event: ClickEvent):
        logger.info("Publishing analytics event")
        await self._publish(event.model_dump_json(), self.settings.ANALYTICS_ROUTING_KEY)

class QrJobProducer(BaseProducer):
    async def publish(self, short_code: str, action: str = "upload", qr_key: str | None = None):
        logger.info("Publishing QR job for %s", short_code)
        event = QrCodeJobEvent(short_code=short_code, action=action, qr_key=qr_key)
        await self._publish(event.model_dump_json(), self.settings.QR_ROUTING_KEY)
        logger.info("Qr Job published :)")
