from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Facility, FacilityType, User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.delete("/commissioner/facility-type/{type_id}")
def delete_commissioner_facility_type(
    type_id: int, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    facility_type = db.query(FacilityType).filter(FacilityType.id == type_id).first()
    if not facility_type:
        raise HTTPException(status_code=404, detail="Facility type not found")

    in_use = db.query(Facility).filter(Facility.facility_type == facility_type.name).first()
    if in_use:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete facility type as it is in use by one or more facilities",
        )

    db.delete(facility_type)
    db.commit()
    return {"message": "Facility type deleted successfully"}
