from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, UtilityBill, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id
from datetime import date

router = APIRouter()


@router.get("/citizen/dash")
def citizen_dashboard(current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('citizen'):
        return {"error": "Citizen access required"}, 403

    pending_bills = db.query(UtilityBill).filter_by(user_id=current_user_id, status='pending').count()
    overdue_bills = db.query(UtilityBill).filter_by(user_id=current_user_id, status='overdue').count()
    total_bills_due = pending_bills + overdue_bills

    upcoming_bookings = db.query(FacilityBooking).filter(
        FacilityBooking.user_id == current_user_id,
        FacilityBooking.status == 'confirmed',
        FacilityBooking.date >= date.today()
    ).count()

    pending_bills_list = db.query(UtilityBill).filter(
        UtilityBill.user_id == current_user_id,
        UtilityBill.status.in_(['pending', 'overdue'])
    ).order_by(UtilityBill.due_date.asc()).limit(5).all()

    bills_data = []
    for bill in pending_bills_list:
        bills_data.append({
            "id": bill.id,
            "bill_type": bill.bill_type,
            "bill_number": bill.bill_number,
            "amount": bill.amount,
            "due_date": bill.due_date.isoformat(),
            "status": bill.status,
        })

    upcoming_bookings_list = db.query(FacilityBooking).filter(
        FacilityBooking.user_id == current_user_id,
        FacilityBooking.status == 'confirmed',
        FacilityBooking.date >= date.today()
    ).order_by(FacilityBooking.date.asc()).limit(5).all()

    bookings_data = []
    for booking in upcoming_bookings_list:
        bookings_data.append({
            "id": booking.id,
            "facility_name": booking.facility.name if booking.facility else "N/A",
            "date": booking.date.isoformat(),
            "booking_reference": booking.booking_reference,
            "amount_paid": booking.amount_paid,
            "status": booking.status,
        })

    return {
        "user_name": user.name,
        "total_bills_due": total_bills_due,
        "upcoming_bookings_count": upcoming_bookings,
        "pending_bills": bills_data,
        "upcoming_bookings": bookings_data
    }
