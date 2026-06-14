from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)