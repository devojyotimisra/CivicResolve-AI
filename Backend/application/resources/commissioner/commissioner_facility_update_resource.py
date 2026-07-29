from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility
from application.helpers.validators import validate_price
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()

@router.put("/commissioner/facility/{facility_id}")
def commissioner_update_facility(
    facility_id: int,
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    facility = db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    if data.get("name"):
        facility.name = data["name"].strip()
    if data.get("facility_type"):
        facility.facility_type = data["facility_type"].strip()
    if data.get("address"):
        facility.address = data["address"].strip()
    if data.get("pincode"):
        facility.pincode = data["pincode"].strip()
    if data.get("price_per_day"):
        is_valid, result = validate_price(data["price_per_day"])
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        facility.price_per_day = result
    if data.get("description") is not None:
        facility.description = data["description"].strip()
    if "is_active" in data:
        facility.is_active = bool(data["is_active"])

    db.commit()

    return {"message": "Facility updated successfully"}
