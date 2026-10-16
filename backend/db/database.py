from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from core import get_database_setting

def get_async_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

settings = get_database_setting()

engine = create_async_engine(
    url=get_async_database_url(settings.DATABASE_URL),
)

Base = declarative_base()
