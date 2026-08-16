from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from db.dependencies import db_dependency
from services import AuthService

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(db: db_dependency, request: UserCreate):
    service = AuthService(db)

    return service.register(request)

@router.post('/login', response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(db:db_dependency, form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
    service = AuthService(db)

    return service.login(form_data.username,
                         form_data.password)
