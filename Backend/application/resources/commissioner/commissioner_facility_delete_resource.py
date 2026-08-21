from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility
from application.middlewares.init_jwt import get_current_user_id

from datetime import date

router = APIRouter()


@router.delete("/commissioner/facility/{facility_id}", response_model=dict[str, str])
def commissioner_delete_facility(
    facility_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    facility = db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
        
    has_future_bookings = any(booking.booked_date >= date.today() for booking in facility.bookings)
    if has_future_bookings:
        raise HTTPException(status_code=400, detail="Cannot delete facility. There are future bookings associated with it.")

    db.delete(facility)
    db.commit()

    return {"message": "Facility deleted"}
