from redis.asyncio import Redis
from backend.core import get_redis_setting

settings = get_redis_setting()

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD.get_secret_value() if settings.REDIS_PASSWORD else None,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
    socket_connect_timeout=1,
    socket_timeout=1,
    health_check_interval=30,
)
