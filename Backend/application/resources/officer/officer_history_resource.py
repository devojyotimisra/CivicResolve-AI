from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/officer/history")
def officer_history(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('field_officer'):
        raise HTTPException(status_code=403, detail="Officer access required")

    # Return ALL complaints assigned to the current officer (active + resolved)
    complaints = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user_id
    ).order_by(Complaint.created_at.desc()).all()

    history = []
    for c in complaints:
        category = db.get(Department, c.department_id) if c.department_id else None
        history.append({
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
            "resolvedAt": c.resolved_at.isoformat() if c.resolved_at else None,
            "createdAt": c.created_at.isoformat() if c.created_at else None,
        })

    return {"history": history}
