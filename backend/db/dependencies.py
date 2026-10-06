from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from .session import get_db

db_dependency = Annotated[AsyncSession, Depends(get_db)]
