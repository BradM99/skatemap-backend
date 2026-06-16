# Database operations for users
from sqlalchemy.orm import Session
from database.models import User


def create_user(db: Session, username: str, email: str, password: str) -> None:
    user = User(username=username, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session) -> list[type[User]]:
    return db.query(User).all()


def delete_user(db: Session, username: str) -> None:
    user = get_user(db, username)
    if user:
        db.delete(user)
        db.commit()
