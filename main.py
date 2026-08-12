from fastapi import FastAPI
from api import api_router
from core.exception_handlers import register_exception_handlers

app = FastAPI(title="Url Shortener API")

register_exception_handlers(app)

app.include_router(api_router)

@app.get('/')
def root():
    return {"message": "Url Shortener API"}