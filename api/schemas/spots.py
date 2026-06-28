from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SpotBase(BaseModel):
    """Base schema for a skate spot, containing core fields shared across operations."""
    name: str
    description: str
    latitude: float
    longitude: float


class SpotCreate(SpotBase):
    """Schema for creating a new spot. Inherits all fields from SpotBase."""
    pass


class SpotUpdate(BaseModel):
    """Schema for partially updating a spot. All fields are optional."""
    name: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class SpotRead(SpotBase):
    """Schema for returning a spot from the API, includes database-generated fields."""
    id: UUID
    created_at: datetime
    created_by: UUID

    model_config = ConfigDict(from_attributes=True)