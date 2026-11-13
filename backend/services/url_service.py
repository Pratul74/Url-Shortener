import logging
import re
import asyncio
from datetime import datetime, timezone, timedelta

from sqlalchemy.exc import IntegrityError

from backend.core.config import get_api_setting
from backend.exceptions import (
    AliasAlreadyExistsException,
    UrlNotFoundException,
    UrlInactiveException,
    UrlExpiredException,
)
from backend.mappers import UrlMapper
from backend.repositories.url_repository import URLRepository
from backend.services.base import BaseService
from backend.services.qr import QrCodeService, QrStorageError
from backend.utils import encode, IDGenerator

logger = logging.getLogger(__name__)

_ALIAS_RE = re.compile(r"^[A-Za-z0-9_-]{3,10}$")
_RESERVED = {"api", "docs", "redoc", "openapi", "health", "login", "register", "admin", "static"}
_MAX_CODE_RETRIES = 3


class UrlShortenerService(BaseService):
    def __init__(
        self,
        db,
        generator: IDGenerator | None = None,
        qr_service: QrCodeService | None = None,
        settings=None,
    ):
        super().__init__(db)
        self.repo = URLRepository(db)
        self.generator = generator or IDGenerator(worker_id=0)
        self.qr = qr_service
        self.settings = settings or get_api_setting()

    @staticmethod
    def _as_utc(dt: datetime | None) -> datetime | None:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @classmethod
    def _is_expired(cls, expires_at: datetime | None) -> bool:
        expires_at = cls._as_utc(expires_at)
        return expires_at is not None and expires_at <= datetime.now(timezone.utc)

    @staticmethod
    def _validate_alias(alias: str) -> None:
        if not _ALIAS_RE.match(alias) or alias.lower() in _RESERVED:
            raise ValueError("Invalid alias")

    async def _get_owned_url(self, user_id, short_code: str):
        url = await self.repo.get_by_short_code(short_code)
        if not url or url.user_id != user_id:
            raise UrlNotFoundException()
        return url

    async def _attach_qr(self, url) -> None:
        if self.qr is None:
            return
        try:
            key = await self.qr.upload_qr(url.short_code)
            await self.repo.set_qr_key(url, key)
        except QrStorageError:
            logger.warning("QR generation failed for %s; continuing", url.short_code)

    async def create_short_url(
        self,
        original_url: str,
        custom_alias: str | None = None,
        expires_at: datetime | None = None,
        user_id=None,
        with_qr: bool = False,
    ):
        expires_at = self._as_utc(expires_at)
        if expires_at is not None and expires_at <= datetime.now(timezone.utc):
            raise ValueError("expires_at must be in the future")

        if custom_alias:
            self._validate_alias(custom_alias)
            try:
                url = await self.repo.create(
                    id=await self.generator.next_id(),
                    original_url=original_url,
                    short_code=custom_alias,
                    expires_at=expires_at,
                    user_id=user_id,
                )
            except IntegrityError:
                raise AliasAlreadyExistsException()
        else:
            url = None
            for _ in range(_MAX_CODE_RETRIES):
                url_id = await self.generator.next_id()
                try:
                    url = await self.repo.create(
                        id=url_id,
                        original_url=original_url,
                        short_code=encode(url_id),
                        expires_at=expires_at,
                        user_id=user_id,
                    )
                    break
                except IntegrityError:
                    continue
            if url is None:
                raise RuntimeError("Could not allocate a short code")

        return url

    async def get_original_url(self, short_code: str):
        url = await self.repo.get_by_short_code(short_code)
        if not url:
            raise UrlNotFoundException()
        if not url.is_active:
            raise UrlInactiveException()
        if self._is_expired(url.expires_at):
            raise UrlExpiredException()
        return url

    async def record_click(self, short_code: str) -> None:
        await self.repo.increment_clicks_by_code(short_code)

    async def url_details(self, user_id, short_code: str):
        url = await self._get_owned_url(user_id, short_code)
        qr_url = None
        if self.qr and url.qr_key:
            try:
                qr_url = await self.qr.presign_qr(url.qr_key)
            except QrStorageError:
                logger.warning("QR lookup failed for %s", url.short_code)
        return UrlMapper.to_details(url, self.settings.BASE_URL, qr_url=qr_url)

    async def qr_image(self, user_id, short_code: str) -> bytes:
        url = await self._get_owned_url(user_id, short_code)

        if self.qr and url.qr_key:
            try:
                return await self.qr.download_qr(url.qr_key)
            except QrStorageError:
                logger.warning("S3 QR fetch failed for %s; rendering on demand", short_code)

        return await asyncio.to_thread(
            QrCodeService.build_qr_image,
            f"{self.settings.BASE_URL.rstrip('/')}/{url.short_code}",
        )

    async def list_url_by_user(self, user_id, limit: int = 20, offset: int = 0):
        urls = await self.repo.get_all_by_user(user_id, limit=limit, offset=offset)
        return [UrlMapper.to_details(u, self.settings.BASE_URL) for u in urls]

    async def delete_url(self, user_id, short_code: str):
        url = await self._get_owned_url(user_id, short_code)
        await self.repo.deactivate(url)

    async def permanent_delete_url(self, user_id, short_code: str):
        url = await self._get_owned_url(user_id, short_code)
        qr_key = url.qr_key
        await self.repo.permanent_delete_url(url=url)
        return qr_key
