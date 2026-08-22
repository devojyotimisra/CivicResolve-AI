from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Facility, User
from application.helpers.schemas import CommissionerFacilityRequest
from application.helpers.validators import validate_price
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/commissioner/facility/{facility_id}", response_model=dict[str, str])
def commissioner_update_facility(
    facility_id: int,
    data: CommissionerFacilityRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    facility = db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    if data.name:
        facility.name = data.name.strip()
    if data.facility_type:
        facility.facility_type = data.facility_type.strip()
    if data.address:
        facility.address = data.address.strip()
    if data.pincode:
        facility.pincode = data.pincode.strip()
    if data.price_per_day:
        is_valid, result = validate_price(data.price_per_day)
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        facility.price_per_day = result
    if data.capacity is not None:
        facility.capacity = data.capacity
    if data.amenities is not None:
        facility.amenities = data.amenities
    if data.description is not None:
        facility.description = data.description.strip()
    if data.is_active is not None:
        facility.is_active = data.is_active

    db.commit()

    return {"message": "Facility updated successfully"}
