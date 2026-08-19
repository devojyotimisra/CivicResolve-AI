from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility
from application.middlewares.init_jwt import get_current_user_id
from application.helpers.schemas import FacilitySchema, CommissionerSearchRequest

router = APIRouter()


@router.post("/citizen/search", response_model=dict[str, List[FacilitySchema]])
def citizen_search(
    data: CommissionerSearchRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('citizen'):
        raise HTTPException(status_code=403, detail="Citizen access required")

    query_str = (data.query or "").strip()
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

    return {"facilities": facilities}
