from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id):
        return self.db.get(self.model, id)

    def get_all(self):
        return self.db.query(self.model).all()

    def create(self, **kwargs):
        obj = self.model(**kwargs)

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def update(self, obj):
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj):
        self.db.delete(obj)
        self.db.commit()