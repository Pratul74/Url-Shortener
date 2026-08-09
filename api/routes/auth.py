from fastapi import APIRouter, status
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
def login(db:db_dependency, request: LoginRequest):
    service = AuthService(db)

    return service.login(request.email, request.password)
