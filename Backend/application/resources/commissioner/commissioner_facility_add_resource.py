from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility
from application.helpers.validators import validate_name, validate_address, validate_pincode, validate_price
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()

@router.post("/commissioner/facility")
def commissioner_add_facility(
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    is_valid, result = validate_name(data.get("name"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    name = result

    is_valid, result = validate_address(data.get("address"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    address = result

    is_valid, result = validate_pincode(data.get("pincode"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    pincode = result

    # Accept both camelCase (pricePerDay) and snake_case (price_per_day)
    price_raw = data.get("pricePerDay") or data.get("price_per_day")
    is_valid, result = validate_price(price_raw)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    price_per_day = result

    # Accept both camelCase (facilityType) and snake_case (facility_type)
    facility_type = (data.get("facilityType") or data.get("facility_type", "")).strip()
    if not facility_type:
        raise HTTPException(status_code=400, detail="Facility type is required")

    facility = Facility(
        name=name,
        facility_type=facility_type,
        address=address,
        pincode=pincode,
        price_per_day=price_per_day,
        description=data.get("description", "").strip(),
        is_active=True
    )

    db.add(facility)
    db.commit()

    return {"message": f"Facility '{name}' created successfully"}
