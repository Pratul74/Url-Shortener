from .base import BaseRepository
from sqlalchemy.orm import Session
from models import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db:Session):
        super().__init__(User, db)

    def get_by_email(self, email:str):
        return (
            self.db.query(User).filter(User.email == email).first()
            )

    def get_by_username(self, username:str):
        return (
            self.db.query(User).filter(User.username == username).first()
            )

    def exists_by_email(self, email:str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is not None

    def exists_by_username(self, username:str) -> bool:
        return self.db.query(User).filter(User.username == username).first() is None