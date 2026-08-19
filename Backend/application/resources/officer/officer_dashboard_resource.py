from application.helpers.schemas import OfficerDashboardResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/officer/dash", response_model=OfficerDashboardResponse)
def officer_dashboard(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('field_officer'):
        raise HTTPException(status_code=403, detail="Officer access required")

    assigned_complaints = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user_id,
        Complaint.status.notin_(['Resolved', 'Closed'])
    ).order_by(Complaint.created_at.desc()).all()

    for c in assigned_complaints:
        category = db.get(Department, c.department_id) if c.department_id else None
        c.department = category.name if category else c.department

    return {
        "officer_name": user.name,
        "department": user.department,
        "jurisdiction_zone": user.address,
        "assigned_tickets": assigned_complaints,
        "total_assigned": len(assigned_complaints)
    }
