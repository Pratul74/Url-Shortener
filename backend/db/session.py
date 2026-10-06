from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from .database import engine

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

async def close_db():
    await engine.dispose()
