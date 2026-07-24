from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility
from application.helpers.validators import validate_name, validate_address, validate_pincode, validate_price
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/facilities")
def commissioner_facilities_list(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        return {"error": "Commissioner access required"}, 403

    facilities = db.query(Facility).order_by(Facility.name.asc()).all()

    facilities_data = []
    for f in facilities:
        facilities_data.append({
            "id": f.id,
            "name": f.name,
            "facilityType": f.facility_type,
            "address": f.address,
            "pincode": f.pincode,
            "pricePerDay": f.price_per_day,
            "capacity": f.capacity,
            "description": f.description,
            "amenities": f.amenities,
            "isActive": f.is_active,
        })

    return {"facilities": facilities_data}

