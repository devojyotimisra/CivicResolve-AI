from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import FacilityBooking, User
from application.helpers.schemas import FacilityBookingSchema
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/citizen/bookings", response_model=dict[str, List[FacilityBookingSchema]])
def citizen_bookings_list(
    current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("citizen"):
        raise HTTPException(status_code=403, detail="Citizen access required")

    bookings = (
        db.query(FacilityBooking)
        .filter_by(user_id=current_user_id)
        .order_by(FacilityBooking.booked_date.desc())
        .all()
    )
    return {"bookings": bookings}
