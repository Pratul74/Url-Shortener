from redis import Redis as redis
from config import settings

redis_client=redis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf-8",
    decode_responses=True,
    max_connection=20,
)

