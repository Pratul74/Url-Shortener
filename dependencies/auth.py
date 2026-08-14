from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import Annotated
from models import User
from exceptions import InvalidCredentialsException
from repositories import UserRepository
from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import decode_access_token


CurrentUser=Annotated[User, Depends[get_current_user]]

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload=decode_access_token(token)

        user_id=payload.get('sub')

        if user_id is None:
            raise InvalidCredentialsException()

    except JWTError:
        raise InvalidCredentialsException()

    repo = UserRepository(db)

    user = repo.get_by_id(user_id)

    if user is None:
        raise InvalidCredentialsException()

    return user