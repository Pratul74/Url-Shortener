from db.dependencies import db_dependency
from services.url_service import UrlShortenerService
from fastapi import APIRouter, status
from core.config import settings
from schemas.url import UrlCreate, UrlResponse

router = APIRouter(
    prefix='/api/v1',
    tags=["Url Shortener"]
)

@router.post('shorten/', response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(db: db_dependency, request: UrlCreate):
    url_service = UrlShortenerService(db)

    url = url_service.create_short_url(original_url=str(request.original_url), custom_alias=request.custom_alias, expires_at=request.expires_at)

    return UrlResponse(
                       id=str(url.id), 
                       original_url=str(url.original_url), 
                       short_code=url.short_code, 
                       short_url=f"{settings.BASE_URL}/{url.short_code}",
                       clicks=0,
                       created_at=url.created_at,
                       expires_at=url.expires_at
                       )