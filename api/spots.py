import shutil
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from api.schemas import SpotCreate, ApiResponse
from config import Settings
from database import spot_db, images_db
from database.db import get_db

router = APIRouter(prefix="/spots", tags=["spots"])

@router.get("/", response_model=ApiResponse, status_code=HTTPStatus.OK)
def get_all_spots(db: Session = Depends(get_db)):
    """
    Returns a sequence of all spots in the database.
    """
    spots = spot_db.get_all_spots(db)
    return ApiResponse(message="Spots Retrieved", data=spots)


@router.post("/", response_model=ApiResponse, status_code=HTTPStatus.CREATED)
def create_spot(spot: SpotCreate, db: Session = Depends(get_db)):
    """
    Creates a new spot in the database.
    """
    spot = spot_db.create_spot(db, spot)
    return ApiResponse(message="Spot Created", data=spot)


@router.get("/{spot_id}", response_model=ApiResponse, status_code=HTTPStatus.OK)
def get_spot(spot_id: UUID, db: Session = Depends(get_db)):
    """
    Gets a spot from the database using the spot_id.
    Raises 404 if spot does not exist.
    """
    spot = spot_db.get_spot(db, spot_id)
    return ApiResponse(message="Spot Retrieved", data=spot)


@router.get("/{spot_id}/images", response_model=ApiResponse, status_code=HTTPStatus.OK)
def get_spot_images(spot_id: UUID, db: Session = Depends(get_db)):
    """
    Gets all images for a specific spot.
    Raises 404 if spot does not exist.
    """
    images = images_db.get_spot_images(db, spot_id)
    return ApiResponse(message="Images Retrieved", data=images)


@router.post("/{spot_id}/images", response_model=ApiResponse, status_code=HTTPStatus.CREATED)
def upload_image(spot_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Uploads a new image for a specific spot.
    Raises 404 if spot does not exist.
    """
    save_dir = Settings.UPLOAD_DIR / str(spot_id)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = images_db.create_spot_image(db, spot_id, str(file_path))
    return ApiResponse(message="Image Created", data=image)


@router.delete("/{spot_id}/images/{image_id}", response_model=ApiResponse, status_code=HTTPStatus.OK)
def delete_image(spot_id: UUID, image_id: UUID, db: Session = Depends(get_db)):
    """
    Deletes an image from a specific spot.
    Raises 404 if spot or image does not exist.
    """
    image = images_db.delete_spot_image(db, spot_id, image_id)
    return ApiResponse(message="Image Deleted", data=image)