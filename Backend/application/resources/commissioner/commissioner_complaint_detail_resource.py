from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department, ComplaintUpdate
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/complaint/{complaint_id}")
def commissioner_complaint_detail(
    complaint_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    complaint = db.query(Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    category = db.query(Department).get(complaint.department_id) if complaint.department_id else None
    officer = db.query(User).get(complaint.assigned_officer_id) if complaint.assigned_officer_id else None

    updates = db.query(ComplaintUpdate).filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.created_at.asc()).all()
    updates_data = [
        {
            "id": u.id,
            "oldStatus": u.old_status,
            "newStatus": u.new_status,
            "note": u.note,
            "updatedBy": u.updated_by.name if u.updated_by else "System",
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
            "departmentId": complaint.department_id,
            "location": complaint.location,
            "submittedPhoto": complaint.submitted_photo,
            "status": complaint.status,
            "severity": complaint.severity,
            "assignedOfficer": officer.name if officer else None,
            "assignedOfficerId": complaint.assigned_officer_id,
            "resolutionPhoto": complaint.resolution_photo,
            "resolutionNote": complaint.resolution_note,
            "createdAt": complaint.created_at.isoformat() if complaint.created_at else None,
            "updatedAt": complaint.updated_at.isoformat() if complaint.updated_at else None,
            "resolvedAt": complaint.resolved_at.isoformat() if complaint.resolved_at else None,
            "closedAt": complaint.closed_at.isoformat() if complaint.closed_at else None,
        },
        "updates": updates_data
    }
