import io
import re
import logging
import asyncio
from contextlib import AsyncExitStack

import aioboto3
import qrcode
from botocore.exceptions import ClientError
from qrcode.constants import ERROR_CORRECT_M

from backend.core.config import get_aws_setting, get_api_setting

logger = logging.getLogger(__name__)

_SHORT_CODE_RE = re.compile(r"^[A-Za-z0-9_-]{1,10}$")


class QrStorageError(Exception):
    """Raised when QR storage (S3) operations fail."""


class QrCodeService:
    def __init__(self, settings=None, api_settings=None):
        self.settings = settings or get_aws_setting()
        self.api_settings = api_settings or get_api_setting()
        self._session = aioboto3.Session()
        self._stack = AsyncExitStack()
        self._s3 = None
        self._lock = asyncio.Lock()

    async def _get_client(self):
        if self._s3 is None:
            async with self._lock:
                if self._s3 is None:
                    kwargs = {"region_name": self.settings.AWS_REGION}
                    if self.settings.ACCESS_KEY and self.settings.SECRET_ACCESS_KEY:
                        kwargs["aws_access_key_id"] = self.settings.ACCESS_KEY
                        kwargs["aws_secret_access_key"] = self.settings.SECRET_ACCESS_KEY
                    self._s3 = await self._stack.enter_async_context(
                        self._session.client("s3", **kwargs)
                    )
        return self._s3

    async def close(self) -> None:
        await self._stack.aclose()
        self._s3 = None


    @staticmethod
    def build_qr_image(url: str) -> bytes:
        qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    _build_qr_image = build_qr_image

    @staticmethod
    def _key_for(short_code: str) -> str:
        if not _SHORT_CODE_RE.match(short_code):
            raise ValueError("Invalid short_code for QR key")
        return f"qr-codes/{short_code}.png"

    async def upload_qr(self, short_code: str) -> str:
        key = self._key_for(short_code)
        short_url = f"{self.api_settings.BASE_URL.rstrip("/")}/{short_code}"
        image_bytes = await asyncio.to_thread(self.build_qr_image, short_url)
        s3 = await self._get_client()
        try:
            await s3.put_object(
                Bucket = self.settings.S3_BUCKET,
                Key = key,
                Body = image_bytes,
                ContentType = "image/png",
                CacheControl = "public, max-age=31536000, immutable",
                ServerSideEncryption = "AES256",
            )
        except ClientError as e:
            logger.exception("QR upload failed for %s", short_code)
            raise QrStorageError("Failed to upload QR code") from e
        return key

    async def presign_qr(self, key: str, expires: int = 3600) -> str:
        s3 = await self._get_client()
        try:
            return await s3.generate_presigned_url(
                "get_object",
                Params = {"Bucket": self.settings.S3_BUCKET, "Key": key},
                ExpiresIn=expires,
            )
        except ClientError as e:
            logger.exception("QR presign failed for %s", key)
            raise QrStorageError("Failed to generate QR URL") from e

    async def delete_qr(self, key: str) -> None:
        s3 = await self._get_client()
        try:
            await s3.delete_object(
                Bucket = self.settings.S3_BUCKET,
                Key = key
            )
        except ClientError as e:
            logger.exception("QR delete failed for %s", key)
            raise QrStorageError("Failed to delete QR code") from e
        
    async def download_qr(self, key: str) -> bytes:
        s3 = await self._get_client()
        try:
            resp = await s3.get_object(Bucket=self.settings.S3_BUCKET, Key=key)
            async with resp["Body"] as stream:
                return await stream.read()
        except ClientError as e:
            logger.exception("QR download failed for %s", key)
            raise QrStorageError("Failed to download QR code") from e


