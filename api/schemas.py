from datetime import datetime

from pydantic import BaseModel
from uuid import UUID


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

    class ConfigDict:
        from_attributes = True


class ImageBase(BaseModel):
    """Base schema for an image, containing the file path."""
    file_path: str


class ImageCreate(ImageBase):
    """Schema for creating a new image record, requires the associated spot ID."""
    spot_id: UUID


class ImageRead(ImageBase):
    """Schema for returning an image from the API, includes database generated fields."""
    id: UUID
    spot_id: UUID
    uploaded_at: datetime

    class ConfigDict:
        from_attributes = True
