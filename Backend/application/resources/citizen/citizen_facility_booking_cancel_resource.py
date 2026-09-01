from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import FacilityBooking, User
from application.helpers.notification_helper import create_notification
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/citizen/bookings/{booking_id}/cancel")
def cancel_facility_booking(
    booking_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("citizen"):
        raise HTTPException(status_code=403, detail="Citizen access required")

    booking = db.get(FacilityBooking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    if booking.status == "Cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    today = date.today()
    if booking.booked_date <= today:
        raise HTTPException(
            status_code=400, detail="Cannot cancel a booking for today or a past date"
        )

    booking.status = "Cancelled"

    create_notification(
        db,
        user_id=current_user_id,
        title="Booking Cancelled",
        message=f"Your booking (Ref: {booking.booking_reference}) for {booking.facility_name} on {booking.booked_date.isoformat()} has been cancelled. The amount of ₹{booking.amount_paid:,.2f} will be refunded.",
        notif_type="info",
    )

    create_notification(
        db,
        target_role="commissioner",
        title="Booking Cancelled",
        message=f"Booking (Ref: {booking.booking_reference}) for {booking.facility_name} on {booking.booked_date.isoformat()} was cancelled by citizen.",
        notif_type="info",
    )

    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="CITIZEN_CANCEL_BOOKING",
            target_id=booking.id,
            details=f"Citizen {user.name} cancelled booking {booking.booking_reference} for facility {booking.facility_name}.",
        )
    )
    db.commit()

    return {"message": "Booking cancelled successfully and refund initiated"}
