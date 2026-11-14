import logging

from backend.db.dependencies import db_dependency
from backend.services.url_service import UrlShortenerService
from backend.services.qr import QrCodeService
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import Response
from pydantic import ValidationError
from backend.mappers import UrlMapper
from backend.core import get_api_setting
from backend.schemas.url import UrlCreate, UrlResponse, UrlInfo
from backend.dependencies import CurrentUser
from backend.messaging.producer import QrJobProducer
from backend.messaging.events import QrAction

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/urls',
    tags=["Snipp the Url Shortener"]
)

settings = get_api_setting()


async def _publish_qr_job(short_code: str, action: QrAction, qr_key: str | None = None) -> None:
    try:
        await QrJobProducer().publish(short_code, action, qr_key)
    except Exception:
        logger.exception("Failed to publish QR %s job for %s", action, short_code)


@router.post('', response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(db: db_dependency, request: UrlCreate, current_user: CurrentUser, background_tasks: BackgroundTasks):
    url_service = UrlShortenerService(db)

    try:
        url = await url_service.create_short_url(
            original_url=str(request.original_url),
            custom_alias=request.custom_alias,
            expires_at=request.expires_at,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    response = UrlMapper.to_response(url, settings.BASE_URL)
    background_tasks.add_task(_publish_qr_job, url.short_code, QrAction.UPLOAD)
    return response

@router.get('/get_all', response_model=list[UrlInfo])
async def get_all_url_by_user(db:db_dependency, current_user:CurrentUser):
    service=UrlShortenerService(db)
    return await service.list_url_by_user(current_user.id)

@router.get('/detail/{short_code}', response_model=UrlInfo)
async def get_url_detail(short_code:str, db:db_dependency, current_user:CurrentUser):
    service = UrlShortenerService(db)

    return await service.url_details(current_user.id, short_code)

@router.get('/qr/{short_code}', response_class=Response)
async def get_qr_code(
    short_code: str,
    db: db_dependency,
    current_user: CurrentUser,
):
    try:
        qr_service = QrCodeService()
    except ValidationError:
        qr_service = None
    try:
        service = UrlShortenerService(db, qr_service=qr_service)
        image = await service.qr_image(current_user.id, short_code)
    finally:
        if qr_service is not None:
            await qr_service.close()
    return Response(
        content=image,
        media_type='image/png',
        headers={'Cache-Control': 'private, max-age=3600'},
    )

@router.delete('/delete/{short_code}')
async def delete_url(db:db_dependency, short_code:str, current_user:CurrentUser):
    service = UrlShortenerService(db)

    await service.delete_url(current_user.id, short_code)

@router.delete('/permanent_delete/{short_code}')
async def permanent_delete_url(db: db_dependency, short_code: str, current_user:CurrentUser, background_tasks: BackgroundTasks):
    service = UrlShortenerService(db)

    qr_key = await service.permanent_delete_url(user_id=current_user.id, short_code=short_code)
    if qr_key:
        background_tasks.add_task(_publish_qr_job, short_code, QrAction.DELETE, qr_key)
