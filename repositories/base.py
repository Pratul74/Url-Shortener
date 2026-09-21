from typing import Generic, TypeVar, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id):
        return await self.db.get(self.model, id)

    async def get_all(self):
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, **kwargs):
        obj = self.model(**kwargs)

        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

        return obj

    async def update(self, obj):
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj):
        await self.db.delete(obj)
        await self.db.commit()
