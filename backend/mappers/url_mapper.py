from backend.models import Url
from backend.schemas import UrlResponse, UrlInfo

class UrlMapper:

    @staticmethod
    def to_response(url: Url, base_url:str) -> UrlResponse:
        base_url = base_url.rstrip("/")
        return UrlResponse(
                            id=str(url.id), 
                            original_url=str(url.original_url), 
                            short_code=url.short_code, 
                            short_url=f"{base_url}/{url.short_code}",
                            clicks=url.clicks,
                            created_at=url.created_at,
                            expires_at=url.expires_at
                            )

    @staticmethod
    def to_details(url: Url, base_url: str, qr_url: str | None = None) -> UrlInfo:
        base_url = base_url.rstrip("/")
        return UrlInfo(
            id=str(url.id),
            original_url=str(url.original_url),
            short_code=url.short_code,
            short_url=f"{base_url}/{url.short_code}",
            clicks=url.clicks,
            is_active=url.is_active,
            created_at=url.created_at,
            expires_at=url.expires_at,
            qr_url=qr_url,
        )
