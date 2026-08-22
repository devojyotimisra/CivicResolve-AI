from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Facility, User
from application.helpers.schemas import CommissionerFacilityRequest
from application.helpers.validators import validate_address, validate_price
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
        is_valid, result = validate_address(data.address)
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        facility.address = result
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

    existing_facility = (
        db.query(Facility)
        .filter(
            Facility.name == facility.name,
            Facility.facility_type == facility.facility_type,
            Facility.address == facility.address,
            Facility.pincode == facility.pincode,
            Facility.id != facility_id,
        )
        .first()
    )
    if existing_facility:
        raise HTTPException(
            status_code=409,
            detail="A facility with the exact name, type, address, and pincode already exists.",
        )

    db.commit()

    return {"message": "Facility updated successfully"}
