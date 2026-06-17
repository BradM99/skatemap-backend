import string
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID

class UserRegister(BaseModel):
    """Schema for registering a new user."""
    username: Annotated[str, Field(min_length=3, max_length=15)]
    email: Annotated[str, Field(min_length=3, max_length=254)]
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        """
        More than 12 chars
        Min 1 Uppercase char
        Min 1 lowercase char
        Min 1 digit
        Min 1 symbol
        """
        if len(value) < 12:
            raise ValueError("Password must be at least 12 characters long")
        if len(value) > 254:
            raise ValueError("Password must be at most 254 characters long")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase character")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase character")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        if not any(c in string.punctuation for c in value):
            raise ValueError("Password must contain at least one symbol")
        return value

class UserLogin(BaseModel):
    """Schema for logging in a user."""
    email: str
    password: str

class UserRead(BaseModel):
    """Schema for returning a user from the API, includes database generated fields."""
    id: UUID
    username: str
    email: str
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)