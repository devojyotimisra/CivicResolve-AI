from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import Complaint, ComplaintUpdate, Department, ComplaintMedia
from application.helpers.schemas import TrackComplaintResponse, ComplaintSchema, ComplaintUpdateSchema

router = APIRouter()


@router.get("/complaint/track/{token}", response_model=TrackComplaintResponse)
def track_complaint(token: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter_by(token=token).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.status == 'Merged' and complaint.master_complaint_id:
        master = db.get(Complaint, complaint.master_complaint_id)
        if master:
            return {"redirect_to_token": master.token}

    category = db.get(Department, complaint.department_id) if complaint.department_id else None

    updates_orm = db.query(ComplaintUpdate).filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.created_at.asc()).all()

    media_records = db.query(ComplaintMedia).filter_by(complaint_id=complaint.id, media_type='photo').all()
    additional_photos = [m.media_url for m in media_records]

    complaint_schema = ComplaintSchema.model_validate({
        "id": complaint.id,
        "token": complaint.token,
        "master_complaint_id": complaint.master_complaint_id,
        "assigned_officer_id": complaint.assigned_officer_id,
        "assigned_officer_name": complaint.assigned_officer_name,
        "department_id": complaint.department_id,
        "department": category.name if category else complaint.department,
        "title": complaint.title,
        "description": complaint.description,
        "location": complaint.location,
        "submitted_photo": complaint.submitted_photo,
        "additional_photos": additional_photos,
        "status": complaint.status,
        "severity": complaint.severity,
        "resolution_photo": complaint.resolution_photo,
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
            "updated_by_name": u.updated_by_name if u.updated_by_name else (u.updated_by.name if u.updated_by else "System"),
            "created_at": u.created_at,
        })
        for u in updates_orm
    ]

    return {"complaint": complaint_schema, "updates": updates_schema}
