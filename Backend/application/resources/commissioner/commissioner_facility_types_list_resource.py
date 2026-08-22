from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import FacilityType, User
from application.helpers.schemas import FacilityTypeSchema
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/facility-types", response_model=List[FacilityTypeSchema])
def get_commissioner_facility_types(
    current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Commissioner access required")

    types = db.query(FacilityType).order_by(FacilityType.name).all()
    return types
