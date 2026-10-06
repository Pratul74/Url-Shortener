from exceptions import (
    AliasAlreadyExistsException,
    InvalidCredentialsException,
    UrlExpiredException,
    UrlInactiveException,
    UrlNotFoundException,
    UserAlreadyExistsException,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(UrlNotFoundException)
    async def url_not_found_handler(request:Request, exc:UrlNotFoundException):
        return JSONResponse(
            status_code=404,
            content={'detail':str(exc)}
        )

    @app.exception_handler(UrlExpiredException)
    async def url_expired_handler(request:Request, exc:UrlExpiredException):
        return JSONResponse(
            status_code=410,
            content={'detail':str(exc)}
        )

    @app.exception_handler(UrlInactiveException)
    async def url_inactive_handler(request:Request, exc:UrlInactiveException):
        return JSONResponse(
            status_code=404,
            content={'detail':str(exc)}
        )

    @app.exception_handler(AliasAlreadyExistsException)
    async def alias_already_exists_handler(request:Request, exc:AliasAlreadyExistsException):
        return JSONResponse(
            status_code=409,
            content={'detail':str(exc)}
        )

    @app.exception_handler(UserAlreadyExistsException)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
        return JSONResponse(
            status_code=409,
            content={'detail': str(exc)}
        )

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
        return JSONResponse(
            status_code=401,
            content={'detail': str(exc)}
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        return JSONResponse(
            status_code=403,
            content={'detail': str(exc)}
        )
