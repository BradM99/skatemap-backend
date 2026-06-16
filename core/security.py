from http import HTTPStatus

from jose import JWTError, jwt
from pwdlib import PasswordHash
from starlette.exceptions import HTTPException

handler = PasswordHash.recommended()

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return handler.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return handler.verify(hashed_password, password)


def create_access_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )