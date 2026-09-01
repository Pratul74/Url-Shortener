from datetime import datetime, timezone
import uuid

from redis.exceptions import RedisError
from sqlalchemy.orm import Session
from sqlalchemy import update

from core.config import settings
from core.redis import redis_client

from models.url import Url
from repositories.base import BaseRepository


class URLRepository(BaseRepository[Url]):
    def __init__(self, db: Session):
        super().__init__(Url, db)
        self.redis_client = redis_client

    def get_all_by_user(self, user_id):
        return self.db.query(Url).filter(Url.user_id == user_id).all()

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
            "id": str(url.id),
            "original_url": url.original_url,
            "short_code": url.short_code,
            # "short_url": f"{settings.BASE_URL}/{url.short_code}",
            "clicks": str(url.clicks),
            "is_active": str(url.is_active),
            "created_at": str(self._datetime_to_iso(url.created_at)),
            "expires_at": str(self._datetime_to_iso(url.expires_at)),
            "user_id": str(url.user_id),
        }

    def _cache_url(self, url: Url) -> None:
        ttl = self._cache_ttl(url)

        if ttl <= 0:
            print("Skipping cache because TTL <= 0")
            return

        key = self._cache_key(url.short_code)

        try:
            pipe = self.redis_client.pipeline()
            pipe.hset(key, mapping=self._cache_payload(url))
            pipe.expire(key, ttl)
            pipe.execute()
            print(f"Cached {key} for {ttl} seconds")
        except RedisError as e:
            print(f"Redis SET failed: {e}")

    def _delete_cached_url(self, short_code: str) -> None:
        try:
            self.redis_client.delete(self._cache_key(short_code))
        except RedisError as e:
            print(f"Redis DELETE failed: {e}")

    def get_by_short_code(self, short_code: str):
        key = self._cache_key(short_code)

        try:
            cached = self.redis_client.hgetall(key)
        except RedisError:
            print("Redis Unavailable. Proceeding without cache.")
            cached = None

        if cached:
            print(f"✅Cache hit: {key}")
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
                print(f"❌ Invalid cache entry: {key}")
                self._delete_cached_url(short_code)

        print(f"⚠️ Cache MISS: {key}")
        url = self.db.query(Url).filter(Url.short_code == short_code).first()

        if url:
            print(f"💾 Writing to cache: {key}")
            self._cache_url(url)

        return url

    def create(self, **kwargs):
        url = super().create(**kwargs)
        self._cache_url(url)

        return url

    def get_by_original_url(self, original_url: str, user_id:int):
        return (
            self.db.query(Url)
            .filter(Url.user_id == user_id)
            .filter(Url.original_url == original_url)
            .first()
        )

    def short_code_exists(self, short_code: str) -> bool:
        return self.get_by_short_code(short_code) is not None

    def increment_clicks(self, url: Url):
        smt = update(Url).where(Url.id == url.id).values(clicks=Url.clicks+1).returning(Url)
        db_url = self.db.execute(smt).scalar_one()
        self.db.commit()
        key = self._cache_key(db_url.short_code)
        try:
            if self.redis_client.exists(key):
                self.redis_client.hincrby(self._cache_key(db_url.short_code), "clicks", 1)
        except RedisError:
            print("Redis Unavailable. Proceeding without cache.")
        return db_url

    def deactivate(self, user_id:int, url: Url):
        if url.user_id != user_id:
            raise PermissionError("You do not own this url.")

        
        smt = update(Url).where(Url.id == url.id).values(is_active=False).returning(Url)
        db_url = self.db.execute(smt).scalar_one()

        self.db.commit()

        self.db.refresh(db_url)

        self._delete_cached_url(db_url.short_code)

        return db_url
