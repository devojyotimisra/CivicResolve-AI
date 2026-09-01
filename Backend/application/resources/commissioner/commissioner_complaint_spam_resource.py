from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import IST, AuditLog, Complaint, ComplaintUpdate, User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/commissioner/complaint/{complaint_id}/spam", response_model=dict[str, str])
def commissioner_mark_spam(
    complaint_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.status == "Spam":
        raise HTTPException(status_code=400, detail="Ticket is already marked as spam.")

    old_status = complaint.status
    complaint.status = "Spam"
    complaint.updated_at = datetime.now(IST)
    complaint.resolution_note = "Marked as Spam by Commissioner"

    if complaint.assigned_officer_id:
        complaint.assigned_officer_id = None
        complaint.assigned_officer_name = None

    complaint.department_id = None
    complaint.department = None

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=current_user_id,
        old_status=old_status,
        new_status="Spam",
        note="Ticket marked as spam by Commissioner.",
    )
    db.add(update)

    audit_log = AuditLog(
        admin_id=current_user_id,
        action_type="MANUAL_MARK_SPAM",
        target_id=complaint.id,
        details=f"Commissioner manually marked ticket {complaint.token} as spam.",
    )
    db.add(audit_log)

    db.commit()

    return {"message": "Complaint marked as spam successfully"}
