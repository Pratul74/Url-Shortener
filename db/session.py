from sqlalchemy.orm import Session, sessionmaker
from database import engine

SessionLocal = sessionmaker(bind= engine, autoflush=True, autocommit = True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()