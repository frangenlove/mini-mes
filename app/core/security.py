from datetime import datetime,timedelta,timezone

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import settings
from app.core.exceptions import UnauthorizedError

_password_hash = PasswordHash.recommended()


def hash_password(raw: str) -> str:
    return _password_hash.hash(raw)

def verify_password(raw: str,hashed: str) -> bool:
    try:
        return _password_hash.verify(raw,hashed)
    except UnknownHashError:
        return False
    

def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id), # 必须为字符串，PyJWT 2.x会校验
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes)
    }
    return jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm)

def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token,settings.secret_key,algorithms=[settings.algorithm])
    except jwt.PyJWKError as exc: # expiration/signature/format
        raise UnauthorizedError("invalid or expired token") from exc
    sub = payload.get("sub")
    if sub is None:
        raise UnauthorizedError("invalid token payload")

    return int(sub)

