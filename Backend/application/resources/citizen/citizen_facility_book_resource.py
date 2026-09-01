import secrets
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Facility, FacilityBooking, User
from application.helpers.notification_helper import create_notification
from application.helpers.schemas import CitizenFacilityBookRequest, CitizenFacilityBookResponse
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


def generate_booking_ref():
    return "BKG-" + secrets.token_urlsafe(6)[:8].upper()


@router.post("/citizen/book_facility/{facility_id}", response_model=CitizenFacilityBookResponse)
def citizen_book_facility(
    facility_id: int,
    data: CitizenFacilityBookRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("citizen"):
        raise HTTPException(status_code=403, detail="Citizen access required")

    if not user.phone or not user.address:
        raise HTTPException(
            status_code=403,
            detail="Please update your profile with a valid phone number and address before booking a facility.",
        )

    facility = db.get(Facility, facility_id)
    if not facility or not facility.is_active:
        raise HTTPException(status_code=404, detail="Facility not found")

    booking_date_str = data.booked_date
    if not booking_date_str:
        raise HTTPException(status_code=400, detail="Date is required")

    try:
        booking_date = date.fromisoformat(str(booking_date_str).strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    today = date.today()
    if booking_date < today:
        raise HTTPException(status_code=400, detail="Cannot book a past date")

    if booking_date > today + timedelta(days=90):
        raise HTTPException(status_code=400, detail="Cannot book more than 90 days in advance")

    existing = (
        db.query(FacilityBooking)
        .filter(
            FacilityBooking.facility_id == facility_id,
            FacilityBooking.booked_date == booking_date,
            FacilityBooking.status != "Cancelled",
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="This date is already booked")

    booking_ref = generate_booking_ref()
    while db.query(FacilityBooking).filter_by(booking_reference=booking_ref).first():
        booking_ref = generate_booking_ref()

    purpose = data.purpose.strip() if data.purpose else ""

    booking = FacilityBooking(
        user_id=current_user_id,
        facility_id=facility_id,
        facility_name=facility.name,
        booked_date=booking_date,
        booking_reference=booking_ref,
        amount_paid=facility.price_per_day,
        payment_ref="TXN-" + secrets.token_hex(5).upper(),
        purpose=purpose,
    )

    db.add(booking)

    create_notification(
        db,
        user_id=current_user_id,
        title="Booking Confirmed",
        message=f"Booking confirmed for {facility.name} on {booking_date.isoformat()}.",
        notif_type="success",
    )
    create_notification(
        db,
        target_role="commissioner",
        title="Facility Booked",
        message=f"New booking: {facility.name} on {booking_date.isoformat()}.",
        notif_type="info",
    )

    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="CITIZEN_BOOK_FACILITY",
            target_id=facility.id,
            details=f"Citizen {user.name} booked facility {facility.name} for {booking_date.isoformat()}.",
        )
    )
    db.commit()
    db.refresh(booking)

    return {"message": "Booking confirmed", "booking": booking}
