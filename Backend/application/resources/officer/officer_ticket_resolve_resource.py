import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, ComplaintUpdate, IST
from application.middlewares.init_jwt import get_current_user_id
from application.helpers.notification_helper import create_notification

router = APIRouter()


@router.post("/officer/ticket/{complaint_id}/resolve")
async def officer_resolve_ticket(
    complaint_id: int,
    resolution_note: Optional[str] = Form(None),
    resolution_photo: Optional[UploadFile] = File(None),
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

    if complaint.status not in ['In Progress', 'On Site']:
        raise HTTPException(status_code=400, detail="Ticket must be in progress or on site to resolve")

    resolution_note_str = resolution_note.strip() if resolution_note else None
    resolution_photo_url = None

    if resolution_photo and resolution_photo.filename:
        upload_dir = os.path.join("uploads", "resolutions")
        os.makedirs(upload_dir, exist_ok=True)
        
        ext = resolution_photo.filename.split(".")[-1] if "." in resolution_photo.filename else "jpg"
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        
        content = await resolution_photo.read()
        with open(filepath, "wb") as f:
            f.write(content)
            
        resolution_photo_url = f"/uploads/resolutions/{filename}"

    old_status = complaint.status
    complaint.status = 'Resolved'
    
    existing_photos = list(complaint.resolution_photos or [])
    if resolution_photo_url:
        existing_photos.append(resolution_photo_url)
    complaint.resolution_photos = existing_photos
    
    complaint.resolution_note = resolution_note_str
    complaint.resolved_at = datetime.now(IST)
    complaint.updated_at = datetime.now(IST)

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=current_user_id,
        old_status=old_status,
        new_status='Resolved',
        note=resolution_note_str or 'Issue resolved by field officer'
    )

    db.add(update)

    create_notification(
        db,
        target_role="commissioner",
        title="Ticket Resolved",
        message=f"Complaint #{complaint.token}: {complaint.title} has been resolved by {user.name}",
        notif_type="success",
    )

    db.commit()

    return {"message": "Ticket resolved successfully", "resolutionPhotos": existing_photos}
