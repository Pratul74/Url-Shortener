from db.dependencies import db_dependency
from services.url_service import UrlShortenerService
from fastapi import APIRouter, status, Depends
from models import User
from typing import Annotated
from mappers import UrlMapper
from fastapi.responses import RedirectResponse
from core.config import settings
from schemas.url import UrlCreate, UrlResponse, UrlInfo
from dependencies import CurrentUser

router = APIRouter(
    prefix='/urls',
    tags=["Url Shortener"]
)


@router.post('', response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(db: db_dependency, request: UrlCreate, current_user: CurrentUser):
    url_service = UrlShortenerService(db)

    url = url_service.create_short_url(original_url=str(request.original_url), custom_alias=request.custom_alias, expires_at=request.expires_at, user_id=current_user.id)

    return UrlMapper.to_response(url, settings.BASE_URL)

@router.get('/get_all', response_model=list[UrlInfo])
def get_all_url_by_user(db:db_dependency, current_user:CurrentUser):
    service=UrlShortenerService(db)
    return service.list_url_by_user(current_user.id)

@router.get('/{short_code}')
def get_original_url(short_code:str, db: db_dependency):
    service = UrlShortenerService(db)

    url = service.get_original_url(short_code)

    return RedirectResponse(url=url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get('/detail/{short_code}', response_model=UrlInfo)
def get_url_detail(short_code:str, db:db_dependency, current_user:CurrentUser):
    service = UrlShortenerService(db)

    return service.url_details(short_code)

@router.delete('/delete/{short_code}')
def delete_url(db:db_dependency, short_code:str):
    service = UrlShortenerService(db)

    service.delete_url(short_code)


