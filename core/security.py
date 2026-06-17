from datetime import datetime, timezone, timedelta
from http import HTTPStatus

from jose import JWTError, jwt
from pwdlib import PasswordHash
from starlette.exceptions import HTTPException

from config import settings

handler = PasswordHash.recommended()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return handler.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return handler.verify(hashed_password, password)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )