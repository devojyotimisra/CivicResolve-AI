from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/officer/dash")
def officer_dashboard(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('field_officer'):
        raise HTTPException(status_code=403, detail="Officer access required")

    # Use Title Case status values matching DB storage
    assigned_complaints = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user_id,
        Complaint.status.notin_(['Resolved', 'Closed'])
    ).order_by(Complaint.created_at.desc()).all()

    tickets = []
    for c in assigned_complaints:
        category = db.query(Department).get(c.department_id) if c.department_id else None
        tickets.append({
            "id": c.id,
            "token": c.token,
            "title": c.title,
            "description": c.description,
            "department": category.name if category else c.department,
            "location": c.location,
            "status": c.status,
            "severity": c.severity,
            "submittedPhoto": c.submitted_photo,
            "resolutionPhoto": c.resolution_photo,
            "resolutionNote": c.resolution_note,
            "createdAt": c.created_at.isoformat() if c.created_at else None,
        })

    return {
        "officer_name": user.name,
        "department": user.department,
        "jurisdiction_zone": user.address,
        "assigned_tickets": tickets,
        "total_assigned": len(tickets)
    }
