import asyncio
import os
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from application.extensions import db_extn
from application.extensions.db_extn import get_db
from application.helpers.ai_service import (
    auto_route_complaint,
    detect_spam,
    find_duplicate_complaints,
    generate_description_from_photo,
    merge_duplicate_descriptions,
    sanitize_complaint,
    translate_text,
)
from application.helpers.models import IST, Complaint, ComplaintUpdate, Department, User
from application.helpers.notification_helper import create_notification
from application.helpers.schemas import AnonymousComplaintResponse
from application.helpers.validators import validate_description, validate_title

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/pjpeg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def generate_tracking_token():
    return "CRA-" + secrets.token_urlsafe(6)[:8].upper()


def _run_ai_pipeline(
    complaint_id: int,
    title: str,
    description: str,
    filepath: str | None,
    photo_url: str | None,
    category_id: int | None,
    location_text: str | None,
):
    asyncio.run(
        _ai_pipeline_async(
            complaint_id, title, description, filepath, photo_url, category_id, location_text
        )
    )


async def _ai_pipeline_async(
    complaint_id: int,
    title: str,
    description: str,
    filepath: str | None,
    photo_url: str | None,
    category_id: int | None,
    location_text: str | None,
):
    db = db_extn.SessionLocal()
    try:
        complaint = db.get(Complaint, complaint_id)
        if not complaint:
            return

        photo_bytes = None
        if filepath and os.path.exists(filepath):
            with open(filepath, "rb") as f:
                photo_bytes = f.read()

        if photo_bytes:
            generated_desc = await generate_description_from_photo(photo_bytes)
            if generated_desc:
                if "No infrastructure issue identified" in generated_desc:
                    complaint.submitted_photos = []
                    db.commit()
                    if filepath and os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except Exception:
                            pass
                else:
                    if not description:
                        description = generated_desc
                    else:
                        description = f"{description}\n\n[Image Analysis: {generated_desc}]"
                    complaint.description = description
                    db.commit()
            elif not description:
                description = "Complaint submitted with photo."
                complaint.description = description
                db.commit()

        spam_result = await detect_spam(title, description)
        if spam_result and spam_result.get("is_spam"):
            db.delete(complaint)
            db.commit()

            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            return

        working_title = title
        working_description = description
        working_location = location_text

        t_title = await translate_text(title, target_lang="en")
        if t_title and t_title.get("detected_language", "en") != "en":
            working_title = t_title.get("translated_text", title)

        t_desc = await translate_text(description, target_lang="en")
        if t_desc and t_desc.get("detected_language", "en") != "en":
            working_description = t_desc.get("translated_text", description)

        if location_text:
            t_loc = await translate_text(location_text, target_lang="en")
            if t_loc and t_loc.get("detected_language", "en") != "en":
                working_location = t_loc.get("translated_text", location_text)
                complaint.location = working_location

        sanitized = await sanitize_complaint(working_title, working_description, working_location)
        if sanitized:
            if sanitized.get("sanitized_title"):
                working_title = sanitized["sanitized_title"]
            if sanitized.get("sanitized_description"):
                working_description = sanitized["sanitized_description"]
            if (
                working_location
                and sanitized.get("sanitized_location")
                and sanitized["sanitized_location"] != "Not provided"
            ):
                working_location = sanitized["sanitized_location"]
                complaint.location = working_location

        complaint.title = working_title
        complaint.description = working_description

        departments = db.query(Department).all()
        dept_names = [d.name for d in departments]
        routing = await auto_route_complaint(
            working_title, working_description, photo_bytes, dept_names
        )

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
        final_status = "Submitted"

        if final_dept_id:
            officers = (
                db.query(User)
                .filter(
                    User.department_id == final_dept_id,
                    User.is_active,
                    User.roles.any(name="field_officer"),
                )
                .all()
            )

            if officers:
                officer_loads = []
                for officer in officers:
                    active_count = (
                        db.query(func.count(Complaint.id))
                        .filter(
                            Complaint.assigned_officer_id == officer.id,
                            Complaint.status.in_(
                                ["Assigned", "En Route", "On Site", "In Progress"]
                            ),
                        )
                        .scalar()
                    )
                    officer_loads.append((officer, active_count))

                best_officer = min(officer_loads, key=lambda x: x[1])[0]
                auto_officer_id = best_officer.id
                auto_officer_name = best_officer.name
                final_status = "Assigned"

        complaint.assigned_officer_id = auto_officer_id
        complaint.assigned_officer_name = auto_officer_name

        cutoff_24h = datetime.now(IST) - timedelta(hours=24)
        cutoff_30d = datetime.now(IST) - timedelta(days=30)

        recent_complaints = (
            db.query(Complaint)
            .filter(
                Complaint.id != complaint_id,
                or_(
                    and_(
                        Complaint.status.in_(
                            [
                                "Submitted",
                                "Assigned",
                                "En Route",
                                "On Site",
                                "In Progress",
                                "Resolved",
                            ]
                        ),
                        Complaint.created_at >= cutoff_24h,
                    ),
                    and_(Complaint.status == "Closed", Complaint.created_at >= cutoff_30d),
                ),
            )
            .order_by(Complaint.created_at.desc())
            .limit(30)
            .all()
        )

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
                {
                    "title": working_title,
                    "description": working_description,
                    "location": working_location or "",
                },
                existing_list,
            )

            if dup_result and dup_result.get("is_duplicate"):
                master_id = dup_result.get("master_id")
                if master_id:
                    master = db.get(Complaint, master_id)
                    if master:
                        if master.status == "Closed":
                            if filepath and os.path.exists(filepath):
                                try:
                                    os.remove(filepath)
                                except Exception:
                                    pass

                            tokens = list(master.related_tokens or [])
                            tokens.append(complaint.token)
                            master.related_tokens = tokens

                            master.updated_at = datetime.now(IST)

                            dup_update = ComplaintUpdate(
                                complaint_id=master.id,
                                updated_by_id=None,
                                old_status=master.status,
                                new_status=master.status,
                                note="Late duplicate report logged. Discarded media and description.",
                            )
                            db.add(dup_update)
                        else:
                            escalated = master.severity != "Critical"
                            master.severity = "Critical"

                            merged_desc = await merge_duplicate_descriptions(
                                master.description, working_description
                            )
                            if merged_desc:
                                master.description = merged_desc
                            else:
                                combined_desc = f"{master.description}\n\n--- Additional Citizen Report ---\n{working_description}"
                                master.description = combined_desc
                                re_sanitized = await sanitize_complaint(
                                    master.title, combined_desc, master.location
                                )
                                if re_sanitized:
                                    if re_sanitized.get("sanitized_title"):
                                        master.title = re_sanitized["sanitized_title"]
                                    if re_sanitized.get("sanitized_description"):
                                        master.description = re_sanitized["sanitized_description"]
                                    if (
                                        master.location
                                        and re_sanitized.get("sanitized_location")
                                        and re_sanitized["sanitized_location"] != "Not provided"
                                    ):
                                        master.location = re_sanitized["sanitized_location"]

                            if photo_url:
                                photos = list(master.submitted_photos or [])
                                if photo_url not in photos:
                                    photos.append(photo_url)
                                master.submitted_photos = photos

                            tokens = list(master.related_tokens or [])
                            tokens.append(complaint.token)
                            master.related_tokens = tokens

                            master.updated_at = datetime.now(IST)

                            note_text = "Additional citizen report merged. Details added."
                            if escalated:
                                note_text += " Severity escalated to Critical."
                            dup_update = ComplaintUpdate(
                                complaint_id=master.id,
                                updated_by_id=None,
                                old_status=master.status,
                                new_status=master.status,
                                note=note_text,
                            )
                            db.add(dup_update)

                        db.delete(complaint)
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
            note=(f"Routed to {ai_dept_name}" if ai_dept_name else "")
            + (f", assigned to {auto_officer_name}" if auto_officer_name else ""),
        )
        db.add(ai_update)

        create_notification(
            db,
            target_role="commissioner",
            title="New Complaint Filed",
            message=f"New complaint: '{complaint.title}'"
            + (f" — routed to {ai_dept_name}" if ai_dept_name else ""),
            notif_type="info",
        )

        if auto_officer_id:
            create_notification(
                db,
                user_id=auto_officer_id,
                title="New Ticket Assigned",
                message=f"Assigned to new complaint: '{complaint.title}'",
                notif_type="info",
            )

        db.commit()

    except Exception as e:
        try:
            complaint = db.get(Complaint, complaint_id)
            if complaint and complaint.status == "Processing":
                complaint.status = "Submitted"
                complaint.updated_at = datetime.now(IST)
                fallback_update = ComplaintUpdate(
                    complaint_id=complaint.id,
                    updated_by_id=None,
                    old_status="Processing",
                    new_status="Submitted",
                    note="AI processing encountered an error. Complaint submitted for manual review.",
                )
                db.add(fallback_update)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.post("/complaint/anonymous", response_model=AnonymousComplaintResponse)
async def file_anonymous_complaint(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    address_text: Optional[str] = Form(None, alias="addressText"),
    category_id: Optional[int] = Form(None, alias="categoryId"),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    is_valid, result = validate_title(title)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    title = result

    if not description and not photo:
        raise HTTPException(
            status_code=400, detail="Description is required if no photo is provided"
        )

    if description:
        is_valid, result = validate_description(description)
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        description = result
    else:
        description = ""

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
                detail=f"Invalid file type '{ext}'. Allowed extensions are: .png, .jpg, .jpeg",
            )

        content_type = (photo.content_type or "").lower().strip()
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid MIME type '{photo.content_type}'. Allowed types are: image/png, image/jpeg",
            )

        content = await photo.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            size_mb = round(len(content) / (1024 * 1024), 2)
            raise HTTPException(
                status_code=400,
                detail=f"File size ({size_mb} MB) exceeds maximum allowed limit of 10 MB",
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
        submitted_photos=[photo_url] if photo_url else [],
        location=location_text,
        status="Processing",
        severity="Normal",
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    initial_update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=None,
        old_status="New",
        new_status="Processing",
        note="Complaint received.",
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
        "complaint_id": complaint.id,
    }
