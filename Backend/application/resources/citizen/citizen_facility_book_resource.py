import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


def generate_booking_ref():
    return "BKG-" + secrets.token_urlsafe(6)[:8].upper()


@router.post("/citizen/book_facility/{facility_id}")
def citizen_book_facility(
    facility_id: int,
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('citizen'):
        raise HTTPException(status_code=403, detail="Citizen access required")

    facility = db.get(Facility, facility_id)
    if not facility or not facility.is_active:
        raise HTTPException(status_code=404, detail="Facility not found")

    booking_date_str = data.get("booked_date") or data.get("bookedDate") or data.get("date")
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

    existing = db.query(FacilityBooking).filter(
        FacilityBooking.facility_id == facility_id,
        FacilityBooking.booked_date == booking_date,
        FacilityBooking.status.in_(['Confirmed', 'confirmed'])
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="This date is already booked")

    booking_ref = generate_booking_ref()
    while db.query(FacilityBooking).filter_by(booking_reference=booking_ref).first():
        booking_ref = generate_booking_ref()

    purpose = (data.get("purpose") or "Community Gathering").strip()

    booking = FacilityBooking(
        user_id=current_user_id,
        facility_id=facility_id,
        booked_date=booking_date,
        booking_reference=booking_ref,
        amount_paid=facility.price_per_day,
        purpose=purpose,
        status='Confirmed'
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking confirmed",
        "booking": {
            "id": booking.id,
            "bookingReference": booking_ref,
            "facilityName": facility.name,
            "bookedDate": booking_date.isoformat(),
            "amountPaid": facility.price_per_day,
            "purpose": purpose,
            "status": "Confirmed"
        }
    }
