from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import api_router
from backend.core.config import get_frontend_setting
from backend.core.exception_handlers import register_exception_handlers
from backend.core.redis import redis_client
from backend.db.session import close_db
from backend.messaging.rabbitmq import RabbitMQConnection


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await RabbitMQConnection.close()
    await redis_client.aclose()
    await close_db()


app = FastAPI(title="Url Shortener API", lifespan=lifespan)

setting = get_frontend_setting()

app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

@app.get('/')
def root():
    return {"message": "Url Shortener API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(api_router)