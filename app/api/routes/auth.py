from fastapi import APIRouter,Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import Token
from app.services import user as user_service
from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token

router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/login",response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    user = user_service.authenticate(db,form.username,form.password)
    if user is None:
        raise UnauthorizedError("incorrect username or password")
    return Token(access_token=create_access_token(user.id))