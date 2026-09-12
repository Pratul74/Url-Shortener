from aio_pika import connect_robust, RobustConnection
from core import settings
import asyncio

class RabbitMQConnection:
    _connection: RobustConnection | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_connection(cls) -> RobustConnection:
        if cls._connection is None or cls._connection.is_closed:
            async with cls._lock:
                if cls._connection is None or cls._connection.is_closed:
                    cls._connection = await connect_robust(
                        host= settings.RABBITMQ_HOST,
                        port= settings.RABBITMQ_PORT,
                        login= settings.RABBITMQ_USER,
                        password= settings.RABBITMQ_PASS
                    )
        return cls._connection