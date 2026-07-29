from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department, ComplaintUpdate
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/officer/ticket/{complaint_id}")
def officer_ticket_detail(
    complaint_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('field_officer'):
        raise HTTPException(status_code=403, detail="Officer access required")

    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.assigned_officer_id != current_user_id:
        raise HTTPException(status_code=403, detail="This ticket is not assigned to you")

    category = db.get(Department, complaint.department_id) if complaint.department_id else None

    updates = db.query(ComplaintUpdate).filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.created_at.asc()).all()
    updates_data = [
        {
            "id": u.id,
            "oldStatus": u.old_status,
            "newStatus": u.new_status,
            "note": u.note,
            "createdAt": u.created_at.isoformat() if u.created_at else None
        }
        for u in updates
    ]

    return {
        "complaint": {
            "id": complaint.id,
            "token": complaint.token,
            "title": complaint.title,
            "description": complaint.description,
            "department": category.name if category else complaint.department,
            "location": complaint.location,
            "submittedPhoto": complaint.submitted_photo,
            "resolutionPhoto": complaint.resolution_photo,
            "resolutionNote": complaint.resolution_note,
            "status": complaint.status,
            "severity": complaint.severity,
            "createdAt": complaint.created_at.isoformat() if complaint.created_at else None,
            "updatedAt": complaint.updated_at.isoformat() if complaint.updated_at else None,
        },
        "updates": updates_data
    }
