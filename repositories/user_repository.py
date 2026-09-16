from .base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, username: str):
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def exists_by_email(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    async def exists_by_username(self, username: str) -> bool:
        return await self.get_by_username(username) is not None
