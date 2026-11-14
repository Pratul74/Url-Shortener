from email_validator import EmailNotValidError, validate_email
from sqlalchemy.exc import IntegrityError

from backend.services.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from backend.mappers import UserMapper
from backend.schemas import UserCreate, UserResponse, TokenResponse
from backend.core.security import hash_password, create_access_token, verify_password
from backend.exceptions import UserAlreadyExistsException, InvalidCredentialsException
from backend.repositories import UserRepository

class AuthService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo=UserRepository(db)

    async def register(self, request:UserCreate) -> UserResponse:
        if await self.repo.exists_by_email(request.email):
            raise UserAlreadyExistsException()

        if await self.repo.exists_by_username(request.username):
            raise UserAlreadyExistsException()

        try:
            user = await self.repo.create(
                username = request.username,
                email = request.email,
                hashed_password = hash_password(request.password)
            )
        except IntegrityError:
            await self.db.rollback()
            raise UserAlreadyExistsException()

        return UserMapper.to_response(user)

    @staticmethod
    def _normalize_email(email: str) -> str:
        try:
            return validate_email(email, check_deliverability=False).normalized
        except EmailNotValidError:
            return email

    async def login(self, email, password) -> TokenResponse:
        user = await self.repo.get_by_email(self._normalize_email(email))

        if not user or not user.is_active:
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
