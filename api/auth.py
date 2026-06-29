from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.schemas.users import UserRead, UserRegister, UserLogin
from core import security
from core.security import verify_password, create_access_token, decode_access_token
from database import users_db
from database.db import get_db
from database.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserRead, status_code=HTTPStatus.CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    if users_db.get_user_by_username(db, user.username):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Username already exists")
    if users_db.get_user_by_email(db, user.email):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Email already exists")

    hashed_password = security.hash_password(user.password)

    return users_db.create_user(db, user.username, user.email, hashed_password)

@router.post("/login", status_code=HTTPStatus.OK)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = users_db.get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token payload")

    user = users_db.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="User not found")

    return user

@router.get("/me", response_model=UserRead, status_code=HTTPStatus.OK)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently authenticated user."""
    return current_user

