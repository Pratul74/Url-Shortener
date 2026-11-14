from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id):
        return await self.db.get(self.model, id)

    async def create(self, **kwargs):
        obj = self.model(**kwargs)

        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

        return obj
