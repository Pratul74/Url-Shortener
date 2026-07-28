from exceptions import UrlExpiredException, UrlInactiveException, UrlNotFoundException, AliasAlreadyExistsException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(UrlNotFoundException)
    async def url_not_found_handler(request:Request, exec:UrlNotFoundException):
        return JSONResponse(
            status_code=404,
            content={'detail':exec.message}
        )

    @app.exception_handler(UrlExpiredException)
    async def url_expired_handler(request:Request, exec:UrlExpiredException):
        return JSONResponse(
            status_code=410,
            content={'detail':exec.message}
        )

    @app.exception_handler(UrlInactiveException)
    async def url_inactive_handler(request:Request, exec:UrlInactiveException):
        return JSONResponse(
            status_code=404,
            content={'detail':exec.message}
        )

    @app.exception_handler(AliasAlreadyExistsException)
    async def alias_already_exists_handler(request:Request, exec:AliasAlreadyExistsException):
        return JSONResponse(
            status_code=409,
            content={'detail':exec.message}
        )
