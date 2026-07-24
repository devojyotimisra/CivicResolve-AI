from fastapi import APIRouter, Depends
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
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('citizen'):
        return {"error": "Citizen access required"}, 403

    booking = db.query(FacilityBooking).get(booking_id)
    if not booking:
        return {"error": "Booking not found"}, 404

    if booking.user_id != current_user_id:
        return {"error": "Access denied"}, 403

    if booking.status == 'cancelled':
        return {"error": "Booking is already cancelled"}, 400

    from datetime import date
    if booking.date < date.today():
        return {"error": "Cannot cancel a past booking"}, 400

    booking.status = 'cancelled'
    db.commit()

    return {"message": "Booking cancelled successfully"}
