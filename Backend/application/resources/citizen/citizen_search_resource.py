from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/citizen/search")
def citizen_search(
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('citizen'):
        return {"error": "Citizen access required"}, 403

    query_str = data.get("query", "").strip()
    if not query_str:
        return {"facilities": []}

    search_term = f"%{query_str}%"

    facilities = db.query(Facility).filter(
        Facility.is_active == True,
        or_(
            Facility.name.ilike(search_term),
            Facility.address.ilike(search_term),
            Facility.facility_type.ilike(search_term),
            Facility.pincode.ilike(search_term),
        )
    ).order_by(Facility.name.asc()).all()

    facilities_data = []
    for f in facilities:
        facilities_data.append({
            "id": f.id,
            "name": f.name,
            "facility_type": f.facility_type,
            "address": f.address,
            "pincode": f.pincode,
            "price_per_day": f.price_per_day,
        })

    return {"facilities": facilities_data}
