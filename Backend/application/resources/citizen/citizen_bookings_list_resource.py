from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/citizen/bookings")
def citizen_bookings_list(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('citizen'):
        raise HTTPException(status_code=403, detail="Citizen access required")

    bookings = db.query(FacilityBooking).filter_by(user_id=current_user_id).order_by(FacilityBooking.booked_date.desc()).all()

    bookings_data = []
    for b in bookings:
        bookings_data.append({
            "id": b.id,
            "facilityName": b.facility.name if b.facility else "N/A",
            "facilityType": b.facility.facility_type if b.facility else None,
            "bookedDate": b.booked_date.isoformat(),
            "bookingReference": b.booking_reference,
            "amountPaid": b.amount_paid,
            "purpose": b.purpose,
            "status": b.status,
            "createdAt": b.created_at.isoformat() if b.created_at else None,
        })

    return {"bookings": bookings_data}
