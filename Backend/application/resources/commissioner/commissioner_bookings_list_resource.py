from typing import List
from application.helpers.schemas import FacilityBookingSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()

@router.get("/commissioner/bookings", response_model=dict[str, List[FacilityBookingSchema]])
def commissioner_bookings_list(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    bookings = db.query(FacilityBooking).order_by(FacilityBooking.booked_date.desc()).all()
    return {"bookings": bookings}
