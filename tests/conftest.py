import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from config import Settings, settings
from database.db import Base, get_db
from database.models import Spot, User
from main import app

TEST_DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/skatemap_test_db"
)

engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after for full isolation."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def temp_upload_dir(tmp_path):
    """Redirect uploads to a temp directory, cleaned up after each test."""
    original = Settings.UPLOAD_DIR
    Settings.UPLOAD_DIR = tmp_path
    yield tmp_path
    Settings.UPLOAD_DIR = original


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db(setup_database):
    """Provide a SQLAlchemy session connected to the test database."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(setup_database):
    """Provide a TestClient connected to the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def spot(db, user):
    """Create and return a test spot in the database."""
    spot = Spot(
        name="Test Spot",
        description="Fixture test spot",
        latitude=51.5074,
        longitude=-0.1278,
        created_by=user.id,
    )
    db.add(spot)
    db.commit()
    db.refresh(spot)
    return spot

@pytest.fixture
def user(db):
    """Create and return a test user in the database."""
    user = User(
        username="username",
        email="email@address.com",
        hashed_password="password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def multiple_users(db):
    users = []
    for i in range(5):
        user = User(
            username=f"username{i}",
            email=f"email{i}@address.com",
            hashed_password="password"
        )
        users.append(user)

    db.add_all(users)
    db.commit()
    return users