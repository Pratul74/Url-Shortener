import uuid

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import Annotated
from backend.models import User
from backend.exceptions import InvalidCredentialsException
from backend.repositories import UserRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_db
from backend.core.security import decode_access_token


oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/auth/login')

async def get_current_user(token:str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload=decode_access_token(token)

        user_id = uuid.UUID(payload.get('sub'))

    except (JWTError, TypeError, ValueError):
        raise InvalidCredentialsException()

    repo = UserRepository(db)

    user = await repo.get_by_id(user_id)

    if user is None or not user.is_active:
        raise InvalidCredentialsException()

    return user

CurrentUser=Annotated[User, Depends(get_current_user)]
