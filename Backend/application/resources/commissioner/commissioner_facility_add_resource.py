from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Facility, User
from application.helpers.schemas import CommissionerFacilityRequest
from application.helpers.validators import (
    validate_address,
    validate_name,
    validate_pincode,
    validate_price,
)
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/facility", response_model=dict[str, str])
def commissioner_add_facility(
    data: CommissionerFacilityRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    is_valid, result = validate_name(data.name)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    name = result

    is_valid, result = validate_address(data.address)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    address = result

    is_valid, result = validate_pincode(data.pincode)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    pincode = result

    price_raw = data.price_per_day
    is_valid, result = validate_price(price_raw)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    price_per_day = result

    facility_type = (data.facility_type or "").strip()
    if not facility_type:
        raise HTTPException(status_code=400, detail="Facility type is required")

    existing_facility = (
        db.query(Facility)
        .filter(
            Facility.name == name,
            Facility.facility_type == facility_type,
            Facility.address == address,
            Facility.pincode == pincode,
        )
        .first()
    )
    if existing_facility:
        raise HTTPException(
            status_code=409,
            detail="A facility with the exact name, type, address, and pincode already exists.",
        )

    facility = Facility(
        name=name,
        facility_type=facility_type,
        address=address,
        pincode=pincode,
        price_per_day=price_per_day,
        capacity=data.capacity,
        amenities=data.amenities,
        description=(data.description or "").strip(),
        is_active=True,
    )

    db.add(facility)
    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="COMMISSIONER_ADD_FACILITY",
            target_id=None,
            details=f"Commissioner {user.name} added facility '{name}'.",
        )
    )
    db.commit()

    return {"message": f"Facility '{name}' created successfully"}
