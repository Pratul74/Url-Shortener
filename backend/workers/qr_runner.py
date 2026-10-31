from backend.workers.qr_worker import QrJobWorker
from backend.db.session import AsyncSessionLocal
from backend.messaging.consumer import QrJobConsumer
import asyncio

async def main():
    worker = QrJobWorker(AsyncSessionLocal)
    consumer = QrJobConsumer(worker)
    await consumer.consume()
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())