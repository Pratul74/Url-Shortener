from models import Url
from core import settings
from schemas import UrlResponse, UrlInfo

class UrlMapper:

    @staticmethod
    def to_response(url: Url) -> UrlResponse:
        return UrlResponse(
                            id=str(url.id), 
                            original_url=str(url.original_url), 
                            short_code=url.short_code, 
                            short_url=f"{settings.BASE_URL}/{url.short_code}",
                            clicks=url.clicks,
                            created_at=url.created_at,
                            expires_at=url.expires_at
                            )

    @staticmethod
    def to_details(url: Url):
        return UrlInfo(
            id=str(url.id),
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=f"{settings.BASE_URL}/{url.short_code}",
            clicks=url.clicks,
            is_active=url.is_active,
            created_at=url.created_at,
            expires_at=url.expires_at
        )