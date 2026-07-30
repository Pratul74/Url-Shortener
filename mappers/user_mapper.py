from models import User
from schemas import UserResponse


class UserMapper:

    @staticmethod
    def to_response(user: User):

        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
        )