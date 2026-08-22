from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Facility, User
from application.helpers.schemas import FacilitySchema
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/citizen/facilities", response_model=dict[str, List[FacilitySchema]])
def citizen_facilities_list(
    current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("citizen"):
        raise HTTPException(status_code=403, detail="Citizen access required")

    facilities = db.query(Facility).order_by(Facility.name.asc()).all()
    return {"facilities": facilities}
