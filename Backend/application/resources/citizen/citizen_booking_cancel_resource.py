from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/citizen/cancel_booking/{booking_id}")
def citizen_cancel_booking(
    booking_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('citizen'):
        raise HTTPException(status_code=403, detail="Citizen access required")

    booking = db.get(FacilityBooking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # RC-2: DB stores 'Cancelled' (Title-Case)
    if booking.status == 'Cancelled':
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    from datetime import date
    # RC-1: model column is booked_date, not date
    if booking.booked_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot cancel a past booking")

    # RC-2: set status with Title-Case to match canonical convention
    booking.status = 'Cancelled'
    db.commit()

    return {"message": "Booking cancelled successfully"}
