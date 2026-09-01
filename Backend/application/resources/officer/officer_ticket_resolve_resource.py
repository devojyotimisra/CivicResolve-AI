import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from application.extensions import db_extn
from application.extensions.db_extn import get_db
from application.helpers.ai_service import (
    detect_spam,
    generate_description_from_photo,
    sanitize_resolution_note,
    translate_text,
    verify_resolution_relevance,
)
from application.helpers.models import IST, AuditLog, Complaint, ComplaintUpdate, User
from application.helpers.notification_helper import create_notification
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


async def _process_resolution_ai(
    complaint_id: int,
    current_user_id: int,
    content: bytes,
    resolution_note_str: str | None,
    old_status: str,
    filepath: str,
    resolution_photo_url: str,
):
    db = db_extn.SessionLocal()
    try:
        complaint = db.get(Complaint, complaint_id)
        if not complaint:
            return

        if resolution_note_str:
            translation = await translate_text(resolution_note_str)
            if translation and translation.get("translated_text"):
                original_note = resolution_note_str
                resolution_note_str = translation["translated_text"]
                complaint.resolution_note = resolution_note_str

                db.add(
                    AuditLog(
                        admin_id=None,
                        action_type="AI_TRANSLATION_SANITIZATION",
                        target_id=complaint.id,
                        details=f"AI translated the resolution note.\nOriginal: {original_note}\nTranslated: {resolution_note_str}",
                    )
                )
                db.commit()

        photo_desc = await generate_description_from_photo(content)
        if photo_desc and "No infrastructure issue or repair identified" in photo_desc:
            _revoke_resolution(
                db,
                complaint,
                old_status,
                resolution_photo_url,
                filepath,
                current_user_id,
                "because no valid civic resolution was detected in the photo.",
            )
            return

        combined_text = resolution_note_str or ""
        if photo_desc:
            combined_text += f"\n[Image Analysis: {photo_desc}]"

        spam_result = await detect_spam("Resolution Note", combined_text)
        if spam_result and spam_result.get("is_spam"):
            _revoke_resolution(
                db,
                complaint,
                old_status,
                resolution_photo_url,
                filepath,
                current_user_id,
                "due to spam or improper resolution.",
            )
            return

        relevance_result = await verify_resolution_relevance(
            complaint.title, complaint.description, combined_text
        )
        if relevance_result and not relevance_result.get("is_valid", True):
            _revoke_resolution(
                db,
                complaint,
                old_status,
                resolution_photo_url,
                filepath,
                current_user_id,
                f"because it does not match the original complaint: {relevance_result.get('reason', 'Mismatched resolution')}",
            )
            return

        if resolution_note_str:
            original_note_before_sanitization = resolution_note_str
            sanitized_note = await sanitize_resolution_note(resolution_note_str)
            if sanitized_note and sanitized_note != original_note_before_sanitization:
                complaint.resolution_note = sanitized_note

                db.add(
                    AuditLog(
                        admin_id=None,
                        action_type="AI_TRANSLATION_SANITIZATION",
                        target_id=complaint.id,
                        details=f"AI sanitized the resolution note.\nOriginal: {original_note_before_sanitization}\nSanitized: {sanitized_note}",
                    )
                )
                db.commit()

    finally:
        db.close()


def _revoke_resolution(
    db, complaint, old_status, resolution_photo_url, filepath, current_user_id, reason
):
    complaint.status = old_status
    if complaint.resolution_photos and resolution_photo_url in complaint.resolution_photos:
        photos = list(complaint.resolution_photos)
        photos.remove(resolution_photo_url)
        complaint.resolution_photos = photos

    complaint.resolution_note = None
    complaint.resolved_at = None

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

    create_notification(
        db,
        user_id=current_user_id,
        title="Resolution Rejected",
        message=f"Resolution for '{complaint.title}' rejected {reason}",
        notif_type="error",
    )

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=None,
        old_status="Resolved",
        new_status=old_status,
        note="Resolution rejected by automated system.",
    )
    db.add(update)

    db.add(
        AuditLog(
            admin_id=None,
            action_type="AI_RESOLUTION_REJECTION",
            target_id=complaint.id,
            details=f"AI rejected field officer resolution {reason}",
        )
    )

    db.commit()


@router.post("/officer/ticket/{complaint_id}/resolve")
async def officer_resolve_ticket(
    complaint_id: int,
    background_tasks: BackgroundTasks,
    resolution_note: Optional[str] = Form(None),
    resolution_photo: Optional[UploadFile] = File(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("field_officer"):
        raise HTTPException(status_code=403, detail="Officer access required")

    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.assigned_officer_id != current_user_id:
        raise HTTPException(status_code=403, detail="This ticket is not assigned to you")

    if complaint.status not in ["In Progress", "On Site"]:
        raise HTTPException(
            status_code=400, detail="Ticket must be in progress or on site to resolve"
        )

    resolution_note_str = resolution_note.strip() if resolution_note else None

    if not resolution_photo or not resolution_photo.filename:
        raise HTTPException(status_code=400, detail="A photo is required to resolve the ticket")

    content = await resolution_photo.read()

    upload_dir = os.path.join("uploads", "resolutions")
    os.makedirs(upload_dir, exist_ok=True)

    ext = resolution_photo.filename.split(".")[-1] if "." in resolution_photo.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    resolution_photo_url = f"/uploads/resolutions/{filename}"

    old_status = complaint.status
    complaint.status = "Resolved"

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
        new_status="Resolved",
        note="Issue resolved by field officer.",
    )
    db.add(update)

    create_notification(
        db,
        target_role="commissioner",
        title="Ticket Resolved",
        message=f"'{complaint.title}' was resolved.",
        notif_type="success",
    )

    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="OFFICER_RESOLVE_TICKET",
            target_id=complaint.id,
            details=f"Field Officer {user.name} resolved ticket {complaint.token}.",
        )
    )
    db.commit()

    background_tasks.add_task(
        _process_resolution_ai,
        complaint_id,
        current_user_id,
        content,
        resolution_note_str,
        old_status,
        filepath,
        resolution_photo_url,
    )

    return {"message": "Ticket resolved successfully", "resolutionPhotos": existing_photos}
