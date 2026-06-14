import shutil
from http import HTTPStatus
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from api.schemas import SpotCreate, SpotRead, ImageRead, SpotUpdate
from config import Settings
from database import spot_db, images_db
from database.db import get_db
from config import MAX_FILE_SIZE

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

router = APIRouter(prefix="/spots", tags=["spots"])


@router.get("/", response_model=list[SpotRead], status_code=HTTPStatus.OK)
def get_all_spots(offset: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    """Returns all spots in the database."""
    return spot_db.get_spots_paginated(db, offset, limit)


@router.post("/", response_model=SpotRead, status_code=HTTPStatus.CREATED)
def create_spot(spot: SpotCreate, db: Session = Depends(get_db)):
    """Creates a new spot."""
    return spot_db.create_spot(db, spot)

@router.put("/{spot_id}", response_model=SpotRead, status_code=HTTPStatus.OK)
def update_spot(spot_id: UUID, spot: SpotUpdate, db: Session = Depends(get_db)):
    """Updates an existing spot by using spot ID, and spot update data."""
    return spot_db.update_spot(db, spot_id, spot)

@router.delete("/{spot_id}", status_code=HTTPStatus.OK)
def delete_spot(spot_id: UUID, db: Session = Depends(get_db)):
    """Deletes an existing spot by using spot ID."""
    spot = spot_db.get_spot(db, spot_id)
    if not spot:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Spot not found")
    return spot_db.delete_spot(db, spot)


@router.get("/{spot_id}", response_model=SpotRead, status_code=HTTPStatus.OK)
def get_spot(spot_id: UUID, db: Session = Depends(get_db)):
    """Gets a spot by ID. Returns 404 if not found."""
    return spot_db.get_spot(db, spot_id)

@router.get("/search/bbox", response_model=list[SpotRead], status_code=HTTPStatus.OK)
def get_spots_by_bounding_box(min_lat: float, max_lat: float, min_lng: float, max_lng: float,
                              db: Session = Depends(get_db)):
    """Gets spots within a bounding box."""
    return spot_db.get_spots_by_bounding_box(db, min_lat, max_lat, min_lng, max_lng)


@router.get("/{spot_id}/images", response_model=list[ImageRead], status_code=HTTPStatus.OK)
def get_spot_images(spot_id: UUID, db: Session = Depends(get_db)):
    """Gets all images for a spot. Returns 404 if spot not found."""
    return images_db.get_spot_images(db, spot_id)


@router.post("/{spot_id}/images", response_model=ImageRead, status_code=HTTPStatus.CREATED)
async def upload_image(spot_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads an image to a spot. Returns 404 if spot not found. Checks size and file type."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    save_dir = Settings.UPLOAD_DIR / str(spot_id)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / file.filename

    with file_path.open("wb") as buffer:
        buffer.write(contents)

    return images_db.create_spot_image(db, spot_id, str(file_path))


@router.delete("/{spot_id}/images/{image_id}", response_model=ImageRead, status_code=HTTPStatus.OK)
def delete_image(spot_id: UUID, image_id: UUID, db: Session = Depends(get_db)):
    """Deletes an image from a spot and removes the file from disk."""
    image = images_db.delete_spot_image(db, spot_id, image_id)
    file_path = Path(image.file_path)
    if file_path.exists():
        file_path.unlink()
    return image
