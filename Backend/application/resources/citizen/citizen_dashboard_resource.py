from application.helpers.schemas import CitizenDashboardResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, UtilityBill, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id
from datetime import date

router = APIRouter()


@router.get("/citizen/dash", response_model=CitizenDashboardResponse)
def citizen_dashboard(current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('citizen'):
        raise HTTPException(status_code=403, detail="Citizen access required")

    pending_bills = db.query(UtilityBill).filter_by(user_id=current_user_id, status='Pending').count()
    overdue_bills = db.query(UtilityBill).filter_by(user_id=current_user_id, status='Overdue').count()
    total_bills_due = pending_bills + overdue_bills

    upcoming_bookings = db.query(FacilityBooking).filter(
        FacilityBooking.user_id == current_user_id,
        FacilityBooking.booked_date >= date.today()
    ).count()

    pending_bills_list = db.query(UtilityBill).filter(
        UtilityBill.user_id == current_user_id,
        UtilityBill.status.in_(['Pending', 'Overdue'])
    ).order_by(UtilityBill.due_date.asc()).limit(5).all()

    upcoming_bookings_list = db.query(FacilityBooking).filter(
        FacilityBooking.user_id == current_user_id,
        FacilityBooking.booked_date >= date.today()
    ).order_by(FacilityBooking.booked_date.asc()).limit(5).all()

    return {
        "user_name": user.name,
        "total_bills_due": total_bills_due,
        "upcoming_bookings_count": upcoming_bookings,
        "pending_bills": pending_bills_list,
        "upcoming_bookings": upcoming_bookings_list
    }
