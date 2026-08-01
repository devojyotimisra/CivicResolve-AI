import secrets
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import Complaint, Department, ComplaintUpdate
from application.helpers.validators import validate_title, validate_description

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

    tracking_token = generate_tracking_token()
    while db.query(Complaint).filter_by(token=tracking_token).first():
        tracking_token = generate_tracking_token()

    complaint = Complaint(
        token=tracking_token,
        title=title,
        description=description,
        department_id=category_id,
        submitted_photo=photo_url,
        location=address_text.strip() if address_text else None,
        status='Submitted',
        severity='Normal'
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    initial_update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=None,
        old_status='New',
        new_status='Submitted',
        note='Complaint submitted anonymously'
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
