from datetime import datetime, timezone

from db.dependencies import db_dependency
from services.url_service import UrlShortenerService
from fastapi import APIRouter, BackgroundTasks, Request, status
from mappers import UrlMapper
from fastapi.responses import RedirectResponse
from core.config import settings
from messaging import click_event_producer
from messaging.events import ClickEvent
from schemas.url import UrlCreate, UrlResponse, UrlInfo
from dependencies import CurrentUser

router = APIRouter(
    prefix='/urls',
    tags=["Url Shortener"]
)


@router.post('', response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(db: db_dependency, request: UrlCreate, current_user: CurrentUser):
    url_service = UrlShortenerService(db)

    url = await url_service.create_short_url(original_url=str(request.original_url), custom_alias=request.custom_alias, expires_at=request.expires_at, user_id=current_user.id)

    return UrlMapper.to_response(url, settings.BASE_URL)

@router.get('/get_all', response_model=list[UrlInfo])
async def get_all_url_by_user(db:db_dependency, current_user:CurrentUser):
    service=UrlShortenerService(db)
    return await service.list_url_by_user(current_user.id)

#This route will use redis
@router.get('/{short_code}')
async def get_original_url(
    short_code: str,
    db: db_dependency,
    request: Request,
    background_tasks: BackgroundTasks,
):
    service = UrlShortenerService(db)

    url = await service.get_original_url(short_code)
    background_tasks.add_task(
        publish_click_event,
        ClickEvent(
            url_id=str(url.id),
            short_code=url.short_code,
            ip=request.client.host if request.client else "",
            user_agent=request.headers.get("user-agent", ""),
            referrer=request.headers.get("referer"),
            timestamp=datetime.now(timezone.utc),
        ),
    )

    return RedirectResponse(url=url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

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


async def publish_click_event(click_event: ClickEvent):
    try:
        await click_event_producer.publish(click_event)
    except Exception as exc:
        print(f"Failed to publish click event: {exc}")


