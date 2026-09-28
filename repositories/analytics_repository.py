import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Analytics
from .base import BaseRepository


class AnalyticsRepository(BaseRepository[Analytics]):

    def __init__(self, db: AsyncSession):
        super().__init__(Analytics, db)

    async def get_by_url_id(self, url_id: uuid.UUID) -> Analytics | None:
        result = await self.db.execute(
            select(self.model).where(self.model.url_id == url_id)
        )
        return result.scalar_one_or_none()

    async def create(self, analytics: Analytics):
        self.db.add(analytics)
        await self.db.commit()
        await self.db.refresh(analytics)
        return analytics

    async def update(self, analytics: Analytics):
        await self.db.commit()
        await self.db.refresh(analytics)
        return analytics