import secrets
import os
import uuid
import asyncio
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from application.extensions.db_extn import get_db
from application.extensions import db_extn
from application.helpers.models import Complaint, Department, ComplaintUpdate, User, IST
from application.helpers.validators import validate_title, validate_description
from application.helpers.ai_service import (
    detect_spam,
    translate_text,
    sanitize_complaint,
    auto_route_complaint,
    find_duplicate_complaints,
)
from application.helpers.notification_helper import create_notification

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/pjpeg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def generate_tracking_token():
    return "CRA-" + secrets.token_urlsafe(6)[:8].upper()


def _run_ai_pipeline(complaint_id: int, title: str, description: str, filepath: str | None, photo_url: str | None, category_id: int | None, location_text: str | None):
    asyncio.run(_ai_pipeline_async(complaint_id, title, description, filepath, photo_url, category_id, location_text))


async def _ai_pipeline_async(complaint_id: int, title: str, description: str, filepath: str | None, photo_url: str | None, category_id: int | None, location_text: str | None):
    db = db_extn.SessionLocal()
    try:
        complaint = db.get(Complaint, complaint_id)
        if not complaint:
            return

        spam_result = await detect_spam(title, description)
        if spam_result and spam_result.get("is_spam"):
            complaint.status = 'Rejected'
            spam_reason = spam_result.get("reason", "Flagged as spam")
            complaint.resolution_note = f"Auto-rejected: {spam_reason}"
            complaint.updated_at = datetime.now(IST)

            update = ComplaintUpdate(
                complaint_id=complaint.id,
                updated_by_id=None,
                old_status='Processing',
                new_status='Rejected',
                note=f'Auto-rejected by AI: {spam_reason}',
            )
            db.add(update)
            db.commit()

            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            return

        working_title = title
        working_description = description

        t_title = await translate_text(title, target_lang="en")
        if t_title and t_title.get("detected_language", "en") != "en":
            working_title = t_title.get("translated_text", title)

        t_desc = await translate_text(description, target_lang="en")
        if t_desc and t_desc.get("detected_language", "en") != "en":
            working_description = t_desc.get("translated_text", description)

        sanitized = await sanitize_complaint(working_description)
        if sanitized and sanitized.get("sanitized_text"):
            working_description = sanitized["sanitized_text"]

        complaint.title = working_title
        complaint.description = working_description

        departments = db.query(Department).all()
        dept_names = [d.name for d in departments]

        photo_bytes = None
        if filepath and os.path.exists(filepath):
            with open(filepath, "rb") as f:
                photo_bytes = f.read()

        routing = await auto_route_complaint(working_title, working_description, photo_bytes, dept_names)

        ai_dept_id = None
        ai_dept_name = None
        if routing and routing.get("department"):
            matched = next((d for d in departments if d.name == routing["department"]), None)
            if matched:
                ai_dept_id = matched.id
                ai_dept_name = matched.name

        final_dept_id = ai_dept_id or category_id
        if final_dept_id:
            complaint.department_id = final_dept_id
            if ai_dept_name:
                complaint.department = ai_dept_name

        auto_officer_id = None
        auto_officer_name = None
        final_status = 'Submitted'

        if final_dept_id:
            officers = db.query(User).filter(
                User.department_id == final_dept_id,
                User.is_active == True,
                User.roles.any(name='field_officer')
            ).all()

            if officers:
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
                final_status = 'Assigned'

        complaint.assigned_officer_id = auto_officer_id
        complaint.assigned_officer_name = auto_officer_name

        cutoff = datetime.now(IST) - timedelta(hours=24)

        recent_complaints = db.query(Complaint).filter(
            Complaint.id != complaint_id,
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
                {"title": working_title, "description": working_description, "location": location_text or ""},
                existing_list,
            )

            if dup_result and dup_result.get("is_duplicate"):
                master_id = dup_result.get("master_id")
                if master_id:
                    master = db.get(Complaint, master_id)
                    if master:
                        master.severity = 'Critical'
                        master.updated_at = datetime.now(IST)

                        if photo_url and not master.submitted_photo:
                            master.submitted_photo = photo_url
                        elif photo_url and filepath and os.path.exists(filepath):
                            os.remove(filepath)

                        complaint.status = 'Duplicate'
                        complaint.resolution_note = f'Duplicate of complaint #{master.token}'
                        complaint.updated_at = datetime.now(IST)

                        dup_update = ComplaintUpdate(
                            complaint_id=complaint.id,
                            updated_by_id=None,
                            old_status='Processing',
                            new_status='Duplicate',
                            note=f'Identified as duplicate of {master.token}. Master escalated to Critical.',
                        )
                        db.add(dup_update)
                        db.commit()
                        return

        old_status = complaint.status
        complaint.status = final_status
        complaint.updated_at = datetime.now(IST)

        ai_update = ComplaintUpdate(
            complaint_id=complaint.id,
            updated_by_id=None,
            old_status=old_status,
            new_status=final_status,
            note='AI processing completed' + (f' — routed to {ai_dept_name}' if ai_dept_name else '') + (f', assigned to {auto_officer_name}' if auto_officer_name else ''),
        )
        db.add(ai_update)

        create_notification(
            db,
            target_role="commissioner",
            title="New Complaint Filed",
            message=f"Complaint #{complaint.token}: {complaint.title}" + (f" — routed to {ai_dept_name}" if ai_dept_name else ""),
            notif_type="info",
        )

        if auto_officer_id:
            create_notification(
                db,
                user_id=auto_officer_id,
                title="New Ticket Assigned",
                message=f"You have been auto-assigned to complaint #{complaint.token}: {complaint.title}",
                notif_type="info",
            )

        db.commit()

    except Exception as e:
        try:
            complaint = db.get(Complaint, complaint_id)
            if complaint and complaint.status == 'Processing':
                complaint.status = 'Submitted'
                complaint.updated_at = datetime.now(IST)
                fallback_update = ComplaintUpdate(
                    complaint_id=complaint.id,
                    updated_by_id=None,
                    old_status='Processing',
                    new_status='Submitted',
                    note='AI processing encountered an error. Complaint submitted for manual review.',
                )
                db.add(fallback_update)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.post("/complaint/anonymous")
async def file_anonymous_complaint(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str = Form(...),
    category_id: int = Form(None),
    address_text: str = Form(None),
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

    location_text = address_text.strip() if address_text else None

    tracking_token = generate_tracking_token()
    while db.query(Complaint).filter_by(token=tracking_token).first():
        tracking_token = generate_tracking_token()

    complaint = Complaint(
        token=tracking_token,
        title=title,
        description=description,
        department_id=category_id,
        submitted_photo=photo_url,
        location=location_text,
        status='Processing',
        severity='Normal',
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    initial_update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=None,
        old_status='New',
        new_status='Processing',
        note='Complaint received. AI analysis in progress.',
    )
    db.add(initial_update)
    db.commit()

    background_tasks.add_task(
        _run_ai_pipeline,
        complaint.id,
        title,
        description,
        filepath,
        photo_url,
        category_id,
        location_text,
    )

    return {
        "message": "Complaint filed successfully",
        "tracking_token": tracking_token,
        "trackingToken": tracking_token,
        "complaint_id": complaint.id,
        "complaintId": complaint.id,
    }
