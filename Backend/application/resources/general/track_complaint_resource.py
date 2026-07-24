from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import Complaint, ComplaintUpdate, Department

router = APIRouter()


@router.get("/complaint/track/{token}")
def track_complaint(token: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter_by(tracking_token=token).first()

    if not complaint:
        return {"error": "Complaint not found"}, 404

    category = db.query(Department).get(complaint.department_id) if complaint.department_id else None

    updates = db.query(ComplaintUpdate).filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.created_at.asc()).all()

    updates_data = []
    for update in updates:
        updates_data.append({
            "id": update.id,
            "old_status": update.old_status,
            "new_status": update.new_status,
            "notes": update.notes,
            "created_at": update.created_at.isoformat() if update.created_at else None
        })

    return {
        "complaint": {
            "id": complaint.id,
            "tracking_token": complaint.tracking_token,
            "title": complaint.title,
            "description": complaint.description,
            "category": category.name if category else None,
            "photo_url": complaint.photo_url,
            "address_text": complaint.address_text,
            "status": complaint.status,
            "priority": complaint.priority,
            "resolution_photo_url": complaint.resolution_photo_url,
            "resolution_notes": complaint.resolution_notes,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
            "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
            "resolved_at": complaint.resolved_at.isoformat() if complaint.resolved_at else None,
            "closed_at": complaint.closed_at.isoformat() if complaint.closed_at else None,
        },
        "updates": updates_data
    }
