from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department, ComplaintUpdate
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/citizen/complaint/{complaint_id}")
def citizen_complaint_detail(
    complaint_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('citizen'):
        raise HTTPException(status_code=403, detail="Citizen access required")

    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    category = db.get(Department, complaint.department_id) if complaint.department_id else None

    updates = db.query(ComplaintUpdate).filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.created_at.asc()).all()

    updates_data = []
    for update in updates:
        updates_data.append({
            "id": update.id,
            "old_status": update.old_status,
            "new_status": update.new_status,
            "note": update.note,
            "created_at": update.created_at.isoformat() if update.created_at else None
        })

    return {
        "complaint": {
            "id": complaint.id,
            "token": complaint.token,
            "title": complaint.title,
            "description": complaint.description,
            "category": category.name if category else None,
            "submitted_photo": complaint.submitted_photo,
            "location": complaint.location,
            "status": complaint.status,
            "severity": complaint.severity,
            "resolution_photo": complaint.resolution_photo,
            "resolution_note": complaint.resolution_note,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
            "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
            "resolved_at": complaint.resolved_at.isoformat() if complaint.resolved_at else None,
            "closed_at": complaint.closed_at.isoformat() if complaint.closed_at else None,
        },
        "updates": updates_data
    }
