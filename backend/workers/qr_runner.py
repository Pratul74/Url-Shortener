from backend.workers.qr_worker import QrJobWorker
from backend.db.session import AsyncSessionLocal, close_db
from backend.messaging.consumer import QrJobConsumer
from backend.messaging.topology import RabbitMQTopology
from backend.services.qr import QrCodeService
import asyncio
import logging

async def main():
    qr_service = QrCodeService()
    try:
        await RabbitMQTopology.initialize()
        worker = QrJobWorker(AsyncSessionLocal, qr_service)
        consumer = QrJobConsumer(worker)
        await consumer.consume()
        await asyncio.Future()
    finally:
        await qr_service.close()
        await close_db()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
