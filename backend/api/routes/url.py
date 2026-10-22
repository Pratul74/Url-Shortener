from backend.db.dependencies import db_dependency
from backend.services.url_service import UrlShortenerService
from fastapi import APIRouter, status
from backend.mappers import UrlMapper
from backend.core import get_api_setting
from backend.schemas.url import UrlCreate, UrlResponse, UrlInfo
from backend.dependencies import CurrentUser

router = APIRouter(
    prefix='/urls',
    tags=["Snipp the Url Shortener"]
)

settings = get_api_setting()


@router.post('', response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(db: db_dependency, request: UrlCreate, current_user: CurrentUser):
    url_service = UrlShortenerService(db)

    url = await url_service.create_short_url(original_url=str(request.original_url), custom_alias=request.custom_alias, expires_at=request.expires_at, user_id=current_user.id)

    return UrlMapper.to_response(url, settings.BASE_URL)

@router.get('/get_all', response_model=list[UrlInfo])
async def get_all_url_by_user(db:db_dependency, current_user:CurrentUser):
    service=UrlShortenerService(db)
    return await service.list_url_by_user(current_user.id)

@router.get('/detail/{short_code}', response_model=UrlInfo)
async def get_url_detail(short_code:str, db:db_dependency, current_user:CurrentUser):
    service = UrlShortenerService(db)

    return await service.url_details(current_user.id, short_code)

@router.delete('/delete/{short_code}')
async def delete_url(db:db_dependency, short_code:str, current_user:CurrentUser):
    service = UrlShortenerService(db)

    await service.delete_url(current_user.id, short_code)

@router.delete('/permanent_delete/{short_code}')
async def permanent_delete_url(db: db_dependency, short_code: str, current_user:CurrentUser):
    service = UrlShortenerService(db)

    await service.permanent_delete_url(user_id=current_user.id, short_code=short_code)

