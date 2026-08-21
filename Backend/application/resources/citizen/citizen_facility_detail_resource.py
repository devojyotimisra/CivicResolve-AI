from application.helpers.schemas import CitizenFacilityDetailResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/citizen/facility/{facility_id}", response_model=CitizenFacilityDetailResponse)
def citizen_facility_detail(
    facility_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('citizen'):
        raise HTTPException(status_code=403, detail="Citizen access required")

    facility = db.get(Facility, facility_id)
    if not facility or not facility.is_active:
        raise HTTPException(status_code=404, detail="Facility not found")

    today = date.today()
    end_date = today + timedelta(days=90)

    bookings = db.query(FacilityBooking).filter(
        FacilityBooking.facility_id == facility_id,
        FacilityBooking.booked_date >= today,
        FacilityBooking.booked_date <= end_date
    ).all()

    booked_dates = [b.booked_date.isoformat() for b in bookings]

    my_bookings = [b.booked_date.isoformat() for b in bookings if b.user_id == current_user_id]

    return {
        "facility": facility,
        "booked_dates": booked_dates,
        "my_booked_dates": my_bookings
    }
