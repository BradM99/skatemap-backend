from http import HTTPStatus
from uuid import UUID

from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

from database.models import Spot


def get_or_404(db: Session, model, object_id: UUID):
    """
    Get helper that returns a HTTP 404 if the database object can't be found.
    """
    obj = db.get(model, object_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found"
        )
    return obj

def verify_spot_owner(db: Session, spot_id: UUID, user_id: UUID) -> Spot:
    """
    Gets a spot by ID and verifies the given user owns it.
    Returns the spot if ownership checks out, raises 404/403 otherwise.
    """
    spot = get_or_404(db, Spot, spot_id)
    if spot.created_by != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not authorised to modify this spot")
    return spot