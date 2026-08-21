from application.helpers.schemas import CommissionerDashboardResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department, UtilityBill, FacilityBooking
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/dash", response_model=CommissionerDashboardResponse)
def commissioner_dashboard(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    total_complaints = db.query(Complaint).count()

    pending_complaints = db.query(Complaint).filter(
        Complaint.status.in_(['Submitted', 'Assigned', 'En Route', 'On Site', 'In Progress'])
    ).count()
    resolved_complaints = db.query(Complaint).filter_by(status='Resolved').count()
    closed_complaints = db.query(Complaint).filter_by(status='Closed').count()

    critical_complaints = db.query(Complaint).filter(
        Complaint.severity == 'Critical'
    ).count()

    total_officers = db.query(User).filter(User.roles.any(name='field_officer')).count()
    total_citizens = db.query(User).filter(User.roles.any(name='citizen')).count()

    bill_revenue = db.query(func.sum(UtilityBill.amount)).filter_by(status='Paid').scalar() or 0
    booking_revenue = db.query(func.sum(FacilityBooking.amount_paid)).scalar() or 0
    total_revenue = bill_revenue + booking_revenue

    by_category = db.query(
        Department.name,
        func.count(Complaint.id)
    ).join(Complaint, Complaint.department_id == Department.id).group_by(Department.name).all()

    category_data = [{"name": name, "count": count} for name, count in by_category]

    by_status = db.query(
        Complaint.status,
        func.count(Complaint.id)
    ).group_by(Complaint.status).all()

    status_data = [{"status": status, "count": count} for status, count in by_status]

    from datetime import datetime, timedelta

    # Trend calculation for last 7 days
    today = datetime.now().date()
    trend_data = []
    
    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        
        # Tickets filed on this day
        filed = db.query(Complaint).filter(
            func.date(Complaint.created_at) == day_date
        ).count()
        
        # Tickets resolved on this day (status="Resolved" or closed, using resolved_at)
        resolved = db.query(Complaint).filter(
            func.date(Complaint.resolved_at) == day_date
        ).count()
        
        trend_data.append({
            "day": day_date.strftime("%a"),
            "filed": filed,
            "resolved": resolved
        })

    return {
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "resolved_complaints": resolved_complaints,
        "closed_complaints": closed_complaints,
        "critical_complaints": critical_complaints,
        "total_officers": total_officers,
        "total_citizens": total_citizens,
        "total_revenue": total_revenue,
        "bill_revenue": bill_revenue,
        "booking_revenue": booking_revenue,
        "complaints_by_category": category_data,
        "complaints_by_status": status_data,
        "trend": trend_data,
    }
