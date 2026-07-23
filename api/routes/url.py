from db.dependencies import db_dependency
from services.url_service import UrlShortenerService
from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse
from core.config import settings
from schemas.url import UrlCreate, UrlResponse, UrlInfo

router = APIRouter(
    prefix='/urls',
    tags=["Url Shortener"]
)

@router.post('', response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
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

@router.get('/{short_code}')
def get_original_url(short_code:str, db: db_dependency):
    service = UrlShortenerService(db)

    url = service.get_original_url(short_code)

    return RedirectResponse(url=url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get('/detail/{short_code}', response_model=UrlInfo)
def get_url_detail(short_code:str, db:db_dependency):
    service = UrlShortenerService(db)

    return service.url_details(short_code)

@router.delete('/delete/{short_code}')
def delete_url(db:db_dependency, short_code:str):
    service = UrlShortenerService(db)

    service.delete_url(short_code)

@router.get('/get_all')
def get_all_url(db:db_dependency):
    service=UrlShortenerService(db)
    return service.list_url()


