import logging

from backend.messaging.events import QrCodeJobEvent, QrAction
from backend.services.qr import QrCodeService
from backend.repositories.url_repository import URLRepository

logger = logging.getLogger(__name__)

class QrJobWorker:
    def __init__(self, session_factory, qr_service: QrCodeService):
        self.session_factory = session_factory
        self.qr = qr_service

    async def process_job(self, job: QrCodeJobEvent) -> None:
        if job.action == QrAction.DELETE:
            if job.qr_key:
                await self.qr.delete_qr(job.qr_key)
            return
        if job.action == QrAction.UPLOAD:
            logger.info("Qr code upload started...")
            async with self.session_factory() as db:
                repo = URLRepository(db)
                url = await repo.get_by_short_code(job.short_code)
                if url is None:
                    logger.warning("Skipping QR upload for missing url %s", job.short_code)
                    return
                if not url.is_active or url.qr_key:
                    return
                key = await self.qr.upload_qr(url.short_code)
                await repo.set_qr_key(url, key)
                logger.info("Qr code with key: %s, uploaded successfully", key)
            return
        raise ValueError(f"Unknown QR action: {job.action}")
