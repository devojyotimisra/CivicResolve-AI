from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department, ComplaintUpdate
from application.middlewares.init_jwt import get_current_user_id
from application.helpers.schemas import OfficerTicketDetailResponse, ComplaintSchema, ComplaintUpdateSchema

router = APIRouter()


@router.get("/officer/ticket/{complaint_id}", response_model=OfficerTicketDetailResponse)
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

    updates_orm = db.query(ComplaintUpdate).filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.created_at.asc()).all()



    complaint_schema = ComplaintSchema.model_validate({
        "id": complaint.id,
        "token": complaint.token,
        "related_tokens": complaint.related_tokens or [],
        "assigned_officer_id": complaint.assigned_officer_id,
        "assigned_officer_name": complaint.assigned_officer_name,
        "department_id": complaint.department_id,
        "department": category.name if category else complaint.department,
        "title": complaint.title,
        "description": complaint.description,
        "location": complaint.location,
        "submitted_photos": complaint.submitted_photos or [],
        "status": complaint.status,
        "severity": complaint.severity,
        "resolution_photos": complaint.resolution_photos or [],
        "resolution_note": complaint.resolution_note,
        "created_at": complaint.created_at,
        "updated_at": complaint.updated_at,
        "resolved_at": complaint.resolved_at,
        "closed_at": complaint.closed_at,
    })

    updates_schema = [
        ComplaintUpdateSchema.model_validate({
            "id": u.id,
            "old_status": u.old_status,
            "new_status": u.new_status,
            "note": u.note,
            "created_at": u.created_at,
        })
        for u in updates_orm
    ]

    return {"complaint": complaint_schema, "updates": updates_schema}
