from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import IST, AuditLog, Complaint, ComplaintUpdate, User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/complaints/{complaint_id}/unmerge")
def commissioner_unmerge_complaint(
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

    if complaint.status != "Duplicate":
        raise HTTPException(status_code=400, detail="Only Duplicate tickets can be unmerged.")

    master = db.query(Complaint).filter(Complaint.related_tokens.contains(complaint.token)).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master ticket not found for this duplicate.")

    tokens = list(master.related_tokens or [])
    if complaint.token in tokens:
        tokens.remove(complaint.token)
        master.related_tokens = tokens

    if not master.related_tokens or len(master.related_tokens) == 0:
        master.severity = "Normal"

    master.updated_at = datetime.now(IST)

    complaint.status = "Submitted"
    complaint.resolution_note = None
    complaint.updated_at = datetime.now(IST)

    db.add(
        ComplaintUpdate(
            complaint_id=complaint.id,
            updated_by_id=current_user_id,
            old_status="Duplicate",
            new_status="Submitted",
            note=f"Manually unmerged from master ticket {master.token}",
        )
    )

    db.add(
        ComplaintUpdate(
            complaint_id=master.id,
            updated_by_id=current_user_id,
            old_status=master.status,
            new_status=master.status,
            note=f"Ticket {complaint.token} was manually unmerged from this master.",
        )
    )

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="MANUAL_UNMERGE",
            target_id=complaint.id,
            details=f"Commissioner manually unmerged ticket {complaint.token} from master {master.token}.",
        )
    )

    db.commit()
    return {"message": "Unmerged successfully"}
