from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.schemas import SpotCreate, SpotUpdate
from database.models import Spot
from database.utils import get_or_404


def get_spot(db: Session, spot_id: UUID) -> Spot | None:
    """
    Gets a spot from the database via its spot id.
    """
    return get_or_404(db, Spot, spot_id)


def get_all_spots(db: Session) -> Sequence[Spot]:
    """
    Gets and returns a sequence of all spots in the database.
    """
    return db.execute(select(Spot)).scalars().all()


def get_spots_paginated(db: Session, offset: int = 0, limit: int = 100) -> Sequence[Spot]:
    """
    Gets and returns a limited number of spots from the database.
    Offset is used to skip entries.
    """
    return db.execute(select(Spot).offset(offset).limit(limit)).scalars().all()


def get_spots_by_bounding_box(
    db: Session,
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
) -> Sequence[Spot]:
    """
    Gets all spots within a specified boundary.
    Easily implemented on the frontend with map.getBounds() from Leaflet.js.
    """
    return db.query(Spot).filter(
        Spot.latitude >= min_lat,
        Spot.latitude <= max_lat,
        Spot.longitude >= min_lng,
        Spot.longitude <= max_lng,
    ).all()


def get_by_coords(db: Session, longitude: float, latitude: float) -> Spot | None:
    """
    Gets a Spot from the database via its longitude and latitude.
    """
    statement = select(Spot).where(
        Spot.longitude == longitude,
        Spot.latitude == latitude
    )
    return db.execute(statement).scalar_one_or_none()


def create_spot(db: Session, data: SpotCreate) -> Spot:
    """
    Creates a spot and adds it to the database, returns the spot object.
    """
    spot = Spot(**data.model_dump())
    db.add(spot)
    db.commit()
    db.refresh(spot)
    return spot


def update_spot(db: Session, spot_id: UUID, data: SpotUpdate) -> Spot:
    """
    Updates an existing spot in the database.
    """
    spot = get_or_404(db, Spot, spot_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(spot, field, value)
    db.commit()
    db.refresh(spot)
    return spot


def delete_spot(db: Session, spot: Spot) -> None:
    """
    Deletes a spot from the database.
    """
    db.delete(spot)
    db.commit()


def delete_all_spots(db: Session) -> None:
    db.query(Spot).delete()
    db.commit()