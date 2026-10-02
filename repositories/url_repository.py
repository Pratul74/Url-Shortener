from datetime import datetime, timezone
import uuid

from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from core.config import settings
from core.redis import redis_client

from models.url import Url
from models.analytics import Analytics
from repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)


class URLRepository(BaseRepository[Url]):
    def __init__(self, db: AsyncSession):
        super().__init__(Url, db)
        self.redis_client = redis_client

    async def get_all_by_user(self, user_id: uuid.UUID):
        result = await self.db.execute(select(Url).where(Url.user_id == user_id))
        return result.scalars().all()

    def _cache_key(self, short_code: str) -> str:
        return f"url:{short_code}"

    @staticmethod
    def _datetime_to_iso(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    def _cache_ttl(self, url: Url) -> int:
        ttl = settings.REDIS_CACHE_TTL_SECONDS

        if url.expires_at is None:
            return ttl

        now = datetime.now(timezone.utc)
        expires_at = url.expires_at

        if expires_at.tzinfo is None:
            now = now.replace(tzinfo=None)

        seconds_until_expiry = int((expires_at - now).total_seconds())

        return min(ttl, seconds_until_expiry)

    def _cache_payload(self, url: Url) -> dict[str, str | int | bool | None]:
        return {
            "id": int(url.id),
            "original_url": url.original_url,
            "short_code": url.short_code,
            "clicks": str(url.clicks),
            "is_active": str(url.is_active),
            "created_at": str(self._datetime_to_iso(url.created_at)),
            "expires_at": str(self._datetime_to_iso(url.expires_at)),
            "user_id": str(url.user_id),
        }

    async def _cache_url(self, url: Url) -> None:
        ttl = self._cache_ttl(url)

        if ttl <= 0:
            logger.info("Skipping cache because TTL <= 0")
            return

        key = self._cache_key(url.short_code)

        try:
            pipe = self.redis_client.pipeline()
            pipe.hset(key, mapping=self._cache_payload(url))
            pipe.expire(key, ttl)
            await pipe.execute()
            logger.info(f"Cached {key} for {ttl} seconds")
        except RedisError as e:
            logger.exception(f"Redis SET failed: {e}")

    async def _delete_cached_url(self, short_code: str) -> None:
        try:
            await self.redis_client.delete(self._cache_key(short_code))
        except RedisError as e:
            logger.exception(f"Redis DELETE failed: {e}")

    async def get_by_short_code(self, short_code: str):
        key = self._cache_key(short_code)

        try:
            cached = await self.redis_client.hgetall(key)
        except RedisError:
            logger.exception("Redis Unavailable. Proceeding without cache.")
            cached = None

        if cached:
            logger.info("Cache hit: %s", key)
            try:
                cached["id"] = uuid.UUID(cached["id"])
                cached["clicks"] = int(cached["clicks"])
                cached["is_active"] = cached["is_active"] == "True"
                cached["created_at"] = (datetime.fromisoformat(cached["created_at"])
                                        if cached["created_at"] != "None" else None)
                cached["expires_at"] = (datetime.fromisoformat(cached["expires_at"])
                                        if cached["expires_at"] != "None" else None)
                cached["user_id"] = uuid.UUID(cached["user_id"])
                return Url(**cached)
            except (KeyError, TypeError, ValueError):
                logger.exception("Invalid cache entry: %s", key)
                await self._delete_cached_url(short_code)

        logger.info("Cache Miss: %s", key)
        result = await self.db.execute(select(Url).where(Url.short_code == short_code))
        url = result.scalars().first()

        if url:
            logger.info("Writing to cache: %s", key)
            await self._cache_url(url)

        return url

    async def create(self, **kwargs):
        try:
            url = Url(**kwargs)
            self.db.add(url)
            await self.db.flush()

            self.db.add(Analytics(url_id=url.id))
            await self.db.commit()
            await self.db.refresh(url)
        except Exception as e:
            logger.exception(f"Database transaction failed")
            await self.db.rollback()
            raise
        await self._cache_url(url)

        return url

    async def get_by_original_url(self, original_url: str, user_id:uuid.UUID):
        result = await self.db.execute(
            select(Url)
            .where(Url.user_id == user_id)
            .where(Url.original_url == original_url)
        )
        return result.scalars().first()

    async def short_code_exists(self, short_code: str) -> bool:
        return await self.get_by_short_code(short_code) is not None

    async def increment_clicks(self, url: Url):
        stmt = update(Url).where(Url.id == url.id).values(clicks=Url.clicks+1).returning(Url)
        result = await self.db.execute(stmt)
        db_url = result.scalar_one()
        await self.db.commit()
        key = self._cache_key(db_url.short_code)
        try:
            if await self.redis_client.exists(key):
                await self.redis_client.hincrby(key, "clicks", 1)
        except RedisError:
            logger.exception("Redis Unavailable. Proceeding without cache.")
        return db_url

    async def deactivate(self, user_id:uuid.UUID, url: Url):
        if url.user_id != user_id:
            raise PermissionError("You do not own this url.")

        
        stmt = update(Url).where(Url.id == url.id).values(is_active=False).returning(Url)
        result = await self.db.execute(stmt)
        db_url = result.scalar_one()

        await self.db.commit()

        await self.db.refresh(db_url)

        await self._delete_cached_url(db_url.short_code)

        return db_url

    async def permanent_delete_url(self, user_id: uuid.UUID, url: Url):
        if url.user_id != user_id:
            raise PermissionError("You do not own this url.")
        stmt = delete(Url).where(Url.id == url.id).returning(Url)
        result= await self.db.execute(stmt)
        db_url = result.scalar_one()
        await self.db.commit()

        await self._delete_cached_url(db_url.short_code)
        return db_url
