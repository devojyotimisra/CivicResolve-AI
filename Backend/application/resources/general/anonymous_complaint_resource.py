import secrets
import os
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from application.extensions.db_extn import get_db
from application.helpers.models import Complaint, Department, ComplaintUpdate, User, IST
from application.helpers.validators import validate_title, validate_description
from application.helpers.ai_service import (
    detect_spam,
    translate_text,
    sanitize_complaint,
    auto_route_complaint,
    find_duplicate_complaints,
)

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/pjpeg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def generate_tracking_token():
    return "CRA-" + secrets.token_urlsafe(6)[:8].upper()


@router.post("/complaint/anonymous")
async def file_anonymous_complaint(
    title: str = Form(...),
    description: str = Form(...),
    category_id: int = Form(None),
    address_text: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    is_valid, result = validate_title(title)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    title = result

    is_valid, result = validate_description(description)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    description = result

    if category_id:
        category = db.get(Department, category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category")

    photo_url = None
    filepath = None
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{ext}'. Allowed extensions are: .png, .jpg, .jpeg"
            )

        content_type = (photo.content_type or "").lower().strip()
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid MIME type '{photo.content_type}'. Allowed types are: image/png, image/jpeg"
            )

        content = await photo.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            size_mb = round(len(content) / (1024 * 1024), 2)
            raise HTTPException(
                status_code=400,
                detail=f"File size ({size_mb} MB) exceeds maximum allowed limit of 10 MB"
            )

        upload_dir = os.path.join("uploads", "complaints")
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, "wb") as f:
            f.write(content)

        photo_url = f"/uploads/complaints/{filename}"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  AI PIPELINE — all inline, all best-effort
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # Step 1: SPAM DETECTION — reject immediately if spam
    spam_result = await detect_spam(title, description)
    if spam_result and spam_result.get("is_spam"):
        # Clean up uploaded photo since we're rejecting
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        spam_reason = spam_result.get("reason", "This submission has been flagged as spam or bot-generated")
        spam_type = spam_result.get("spam_type", "spam")
        raise HTTPException(
            status_code=400,
            detail=f"Spam detected: {spam_reason} (type: {spam_type}). Submission blocked."
        )

    # Step 2: TRANSLATION — auto-detect language, translate to English
    t_title = await translate_text(title, target_lang="en")
    if t_title and t_title.get("detected_language", "en") != "en":
        title = t_title.get("translated_text", title)

    t_desc = await translate_text(description, target_lang="en")
    if t_desc and t_desc.get("detected_language", "en") != "en":
        description = t_desc.get("translated_text", description)

    # Step 3: SANITIZATION — remove PII, neutralize tone
    sanitized = await sanitize_complaint(description)
    if sanitized and sanitized.get("sanitized_text"):
        description = sanitized["sanitized_text"]

    # Step 4: AUTO-ROUTING — determine department from text + photo
    departments = db.query(Department).all()
    dept_names = [d.name for d in departments]

    photo_bytes = None
    if filepath and os.path.exists(filepath):
        with open(filepath, "rb") as f:
            photo_bytes = f.read()

    routing = await auto_route_complaint(title, description, photo_bytes, dept_names)

    ai_dept_id = None
    ai_dept_name = None
    if routing and routing.get("department"):
        matched = next((d for d in departments if d.name == routing["department"]), None)
        if matched:
            ai_dept_id = matched.id
            ai_dept_name = matched.name

    # Step 5: AUTO-ASSIGN OFFICER — least-loaded in department
    auto_officer_id = None
    auto_officer_name = None
    auto_status = 'Submitted'

    final_dept_id = ai_dept_id or category_id
    if final_dept_id:
        officers = db.query(User).filter(
            User.department_id == final_dept_id,
            User.is_active == True,
            User.roles.any(name='field_officer')
        ).all()

        if officers:
            # Pick officer with fewest active tickets
            officer_loads = []
            for officer in officers:
                active_count = db.query(func.count(Complaint.id)).filter(
                    Complaint.assigned_officer_id == officer.id,
                    Complaint.status.in_(['Assigned', 'En Route', 'On Site', 'In Progress'])
                ).scalar()
                officer_loads.append((officer, active_count))

            best_officer = min(officer_loads, key=lambda x: x[1])[0]
            auto_officer_id = best_officer.id
            auto_officer_name = best_officer.name
            auto_status = 'Assigned'

    # Step 6: DEDUPLICATION — check recent open complaints (within 24 hours)
    location_text = address_text.strip() if address_text else None
    cutoff = datetime.now(IST) - timedelta(hours=24)

    recent_complaints = db.query(Complaint).filter(
        Complaint.status.in_(['Submitted', 'Assigned', 'En Route', 'On Site', 'In Progress']),
        Complaint.created_at >= cutoff,
    ).order_by(Complaint.created_at.desc()).limit(30).all()

    if recent_complaints:
        existing_list = [
            {
                "id": c.id,
                "token": c.token,
                "title": c.title,
                "description": c.description,
                "location": c.location or "",
            }
            for c in recent_complaints
        ]
        dup_result = await find_duplicate_complaints(
            {"title": title, "description": description, "location": location_text or ""},
            existing_list,
        )

        if dup_result and dup_result.get("is_duplicate"):
            master_id = dup_result.get("master_id")
            if master_id:
                master = db.get(Complaint, master_id)
                if master:
                    # Escalate master to Critical severity
                    master.severity = 'Critical'
                    master.updated_at = datetime.now(IST)
                    db.commit()

                    # Clean up uploaded photo (not needed, master has its own)
                    # We keep the photo — master might not have one
                    # If master has no photo and this one does, update master's photo
                    if photo_url and not master.submitted_photo:
                        master.submitted_photo = photo_url
                        db.commit()
                    elif photo_url and filepath and os.path.exists(filepath):
                        # Master already has a photo, discard this one
                        os.remove(filepath)

                    # Return master's token directly — no new record created
                    return {
                        "message": "Complaint filed successfully",
                        "tracking_token": master.token,
                        "trackingToken": master.token,
                        "complaint_id": master.id,
                        "complaintId": master.id,
                    }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  NOT A DUPLICATE — create complaint normally
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    tracking_token = generate_tracking_token()
    while db.query(Complaint).filter_by(token=tracking_token).first():
        tracking_token = generate_tracking_token()

    complaint = Complaint(
        token=tracking_token,
        title=title,
        description=description,
        department_id=final_dept_id,
        department=ai_dept_name,
        assigned_officer_id=auto_officer_id,
        assigned_officer_name=auto_officer_name,
        submitted_photo=photo_url,
        location=location_text,
        status=auto_status,
        severity='Normal',
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    initial_update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=None,
        old_status='New',
        new_status=auto_status,
        note='Complaint submitted anonymously',
    )
    db.add(initial_update)
    db.commit()

    return {
        "message": "Complaint filed successfully",
        "tracking_token": tracking_token,
        "trackingToken": tracking_token,
        "complaint_id": complaint.id,
        "complaintId": complaint.id,
    }
