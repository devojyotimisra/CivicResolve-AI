from typing import List
from application.helpers.schemas import FacilityBookingSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()

@router.get("/citizen/all_bookings", response_model=dict[str, List[FacilityBookingSchema]])
def citizen_all_bookings_list(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('citizen'):
        raise HTTPException(status_code=403, detail="Citizen access required")

    bookings = db.query(FacilityBooking).all()
    return {"bookings": bookings}
