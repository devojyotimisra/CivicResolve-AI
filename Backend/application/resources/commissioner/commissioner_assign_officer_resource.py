from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, ComplaintUpdate, IST
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/commissioner/assign/{complaint_id}")
def commissioner_assign_officer(
    complaint_id: int,
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    complaint = db.query(Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    officer_id = data.get("officer_id")
    if not officer_id:
        raise HTTPException(status_code=400, detail="Officer ID is required")

    officer = db.query(User).get(officer_id)
    if not officer or not officer.has_role('field_officer'):
        raise HTTPException(status_code=400, detail="Invalid officer")

    if not officer.is_active:
        raise HTTPException(status_code=400, detail="Officer account is deactivated")

    old_status = complaint.status

    complaint.assigned_officer_id = officer_id
    complaint.assigned_officer_name = officer.name

    # Title Case status matching DB storage
    if complaint.status == 'Submitted':
        complaint.status = 'Assigned'

    complaint.updated_at = datetime.now(IST)

    # Update severity (correct attribute name) if provided
    if data.get("severity"):
        if data["severity"] in ['Low', 'Normal', 'High', 'Critical']:
            complaint.severity = data["severity"]

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=current_user_id,
        old_status=old_status,
        new_status=complaint.status,
        note=f"Assigned to officer: {officer.name}"
    )

    db.add(update)
    db.commit()

    return {"message": f"Complaint assigned to {officer.name}"}
