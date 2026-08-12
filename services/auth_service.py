from .base import BaseService
from sqlalchemy.orm import Session
from mappers import UserMapper
from schemas import UserCreate, UserResponse, TokenResponse
from core.security import hash_password, create_access_token, verify_password
from exceptions import UserAlreadyExistsException, InvalidCredentialsException
from repositories import UserRepository

class AuthService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repo=UserRepository(db)

    def register(self, request:UserCreate) -> UserResponse:
        if self.repo.exists_by_email(request.email):
            raise UserAlreadyExistsException()

        if self.repo.exists_by_username(request.username):
            raise UserAlreadyExistsException()

        user = self.repo.create(
            username = request.username,
            email = request.email,
            hashed_password = hash_password(request.password)
        )

        self.db.commit()

        self.db.refresh(user)

        return UserMapper.to_response(user)

    def login(self, email, password) -> TokenResponse:
        user = self.repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsException()
        
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        token = create_access_token(
            {
                'sub':str(user.id)
            }
        )

        return TokenResponse(
            access_token=token,
        )

