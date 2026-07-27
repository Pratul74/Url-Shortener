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

    async def url_expired_handler(request:Request, exec:u)