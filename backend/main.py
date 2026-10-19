from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import api_router
from core.config import get_frontend_setting
from core.exception_handlers import register_exception_handlers

app = FastAPI(title="Url Shortener API")

setting = get_frontend_setting()

allowed_origins = [
    origin.strip()
    for origin in setting.FRONTEND_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router)

@app.get('/')
def root():
    return {"message": "Url Shortener API"}

@app.get("/health")
def health():
    return {"status": "healthy"}