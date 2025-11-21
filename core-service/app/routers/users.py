from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import storage
from app.database import get_db
from app.schemas import User, UserCreate


router = APIRouter()


@router.post("", response_model=User)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Создать пользователя.
    В рамках прототипа пароль нигде не сохраняется и не используется.
    """
    return storage.create_user(db, payload)


@router.get("", response_model=list[User])
async def get_users(db: Session = Depends(get_db)) -> list[User]:
    """Получить список всех пользователей."""
    return storage.list_users(db)



