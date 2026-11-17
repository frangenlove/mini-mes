from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import User

def get_by_username(db: Session,username: str) -> User | None:
    return db.scalar(select(User).where(User.username==username))

def authenticate(db: Session,username: str,password: str) -> User | None:
    user = get_by_username(db,username)
    if user is None or not verify_password(password,user.hashed_password):
        return None
    return user