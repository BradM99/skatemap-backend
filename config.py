from pathlib import Path
from typing import ClassVar

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings

MAX_FILE_SIZE = 10 * 1024 * 1024  # 5MB

class Settings(BaseSettings):
    """Application configuration."""

    ENV: str = Field("development")
    DEBUG: bool = Field(True)

    APP_NAME: str = Field("Skatemap Backend", description="Application name")
    APP_VERSION: str = Field("0.1.0", description="Application version")
    HOSTNAME: str = Field("127.0.0.1", description="Hostname")
    PORT: int = Field(8000, description="Port")

    # Using ClassVar to tell pydantic not to treat this like a model field
    BASE_DIR: ClassVar[Path]  = Path(__file__).resolve().parent #/skatemap
    UPLOAD_DIR: ClassVar[Path] = Path( BASE_DIR / "static/images")

    POSTGRES_USER: str = Field("postgres")
    POSTGRES_PASSWORD: str = Field("2569")
    POSTGRES_HOST: str = Field("localhost")
    POSTGRES_PORT: int = Field(5432)
    POSTGRES_DB: str = Field("skatemap_db")

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn(
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()