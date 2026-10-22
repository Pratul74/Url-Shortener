from redis.asyncio import Redis
from backend.core import get_redis_setting

settings = get_redis_setting()

redis_client = Redis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
    socket_connect_timeout=1,
    socket_timeout=1,
    health_check_interval=30,
)

