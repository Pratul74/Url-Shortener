import logging

from backend.core.config import get_rabbitmq_setting
from backend.messaging.events import QrCodeJobEvent
from backend.services.qr import QrCodeService
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

logger = logging.getLogger(__name__)

class QrJobWorker:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], settings = None):
        self.settings = settings or get_rabbitmq_setting()
        self.session_factory = session_factory

    async def process_job(self, job: QrCodeJobEvent) -> None:
        async with self.session_factory() as db:
            service = QrCodeService(db)
            if job.actions == "delete":
                await service.delete_qr(f"qr-codes/{job.short_code}.png")
            else:
                await service.upload_qr(job.short_code)
            await db.commit()