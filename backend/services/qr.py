import io
import aioboto3
import qrcode
import asyncio
from qrcode.constants import ERROR_CORRECT_M
from backend.core.config import get_aws_setting, get_api_setting
from backend.services.base import BaseService
from backend.repositories.url_repository import URLRepository

class QrCodeService(BaseService):
    def __init__(self, db, settings = None, api_settings= None):
        super().__init__(db)
        self.repo = URLRepository(db)
        self.settings = settings or get_aws_setting()
        self.api_settings = api_settings or get_api_setting()
        self.session = aioboto3.Session()

    @staticmethod
    def _build_qr_image(url: str) -> bytes:
        qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    async def upload_qr(self, short_code: str) -> str:
        short_url = f"{self.api_settings.BASE_URL}/{short_code}"
        key = f"qr-codes/{short_code}.png"
        image_byte = await asyncio.to_thread(self._build_qr_image, short_url)
        async with self.session.client(
            "s3",
            aws_access_key_id=self.settings.ACCESS_KEY,
            aws_secret_access_key=self.settings.SECRET_ACCESS_KEY,
            region_name=self.settings.AWS_REGION,
        ) as s3:
            await s3.put_object(
                Bucket=self.settings.S3_BUCKET,
                Key=key,
                Body=image_byte,
                ContentType="image/png",
            )
        return key

    async def presign_qr(self, key: str, expires: int = 3600) -> str:
        async with self.session.client(
            "s3",
            aws_access_key_id=self.settings.ACCESS_KEY,
            aws_secret_access_key=self.settings.SECRET_ACCESS_KEY,
            region_name=self.settings.AWS_REGION,
        ) as s3:
            return await s3.generate_presigned_url(
                "get_object",
                Params = {"Bucket": self.settings.S3_BUCKET, "Key": key},
                ExpiresIn=expires,
            )

    async def delete_qr(self, key: str) -> None:
        async with self.session.client(
                "s3",
                aws_access_key_id=self.settings.ACCESS_KEY,
                aws_secret_access_key=self.settings.SECRET_ACCESS_KEY,
                region_name=self.settings.AWS_REGION,
        ) as s3:
            await s3.delete_object(
                Bucket = self.settings.S3_BUCKET,
                Key = key
            )




    


    

    

