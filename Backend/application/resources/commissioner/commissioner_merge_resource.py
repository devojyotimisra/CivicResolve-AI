from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import IST, AuditLog, Complaint, ComplaintUpdate, User
from application.helpers.notification_helper import create_notification
from application.helpers.schemas import CommissionerMergeRequest
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/complaints/{complaint_id}/merge")
def commissioner_merge_complaint(
    complaint_id: int,
    data: CommissionerMergeRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    if complaint_id == data.master_id:
        raise HTTPException(status_code=400, detail="Cannot merge a complaint into itself.")

    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    master = db.get(Complaint, data.master_id)
    if not master:
        raise HTTPException(status_code=404, detail="Master complaint not found")

    if master.status in ["Duplicate", "Spam", "Rejected"]:
        raise HTTPException(
            status_code=400, detail=f"Cannot merge into a master ticket that is {master.status}."
        )

    if master.status == "Closed":
        days_since_close = (datetime.now(IST) - master.updated_at).days
        if days_since_close > 30:
            raise HTTPException(
                status_code=400,
                detail="Cannot merge into a ticket that has been closed for more than 30 days.",
            )

    if complaint.status in ["Duplicate", "Spam", "Rejected", "Closed", "Resolved"]:
        raise HTTPException(
            status_code=400, detail=f"Cannot merge a ticket that is currently {complaint.status}."
        )

    old_status = complaint.status

    STATUS_WEIGHT = {
        "Submitted": 0,
        "Assigned": 1,
        "En Route": 2,
        "On Site": 3,
        "In Progress": 4,
        "Resolved": 5,
        "Closed": 6,
    }
    c_weight = STATUS_WEIGHT.get(old_status, -1)
    m_weight = STATUS_WEIGHT.get(master.status, -1)

    if c_weight > m_weight and m_weight != -1 and master.status not in ["Resolved", "Closed"]:
        if (
            master.assigned_officer_id
            and master.assigned_officer_id != complaint.assigned_officer_id
        ):
            create_notification(
                db,
                user_id=master.assigned_officer_id,
                title="Ticket Merged - Stand Down",
                message=f"Your ticket '{master.title}' was merged with an active ticket. Another officer will handle it.",
                notif_type="warning",
            )
        master_old_status = master.status
        master.status = old_status
        master.assigned_officer_id = complaint.assigned_officer_id
        master.assigned_officer_name = complaint.assigned_officer_name
        db.add(
            ComplaintUpdate(
                complaint_id=master.id,
                updated_by_id=current_user_id,
                old_status=master_old_status,
                new_status=master.status,
                note=f"Adopted active progress state ({master.status}) and officer from merged duplicate ticket.",
            )
        )
    elif c_weight > 0 and c_weight <= m_weight:
        if (
            complaint.assigned_officer_id
            and complaint.assigned_officer_id != master.assigned_officer_id
        ):
            create_notification(
                db,
                user_id=complaint.assigned_officer_id,
                title="Ticket Merged - Stand Down",
                message=f"Your ticket '{complaint.title}' was merged into a master ticket handled by someone else. Please stand down.",
                notif_type="warning",
            )

    complaint.status = "Duplicate"
    complaint.resolution_note = f"Manually merged into master ticket {master.token}"
    complaint.assigned_officer_id = None
    complaint.assigned_officer_name = None

    complaint.updated_at = datetime.now(IST)

    tokens = list(master.related_tokens or [])
    if complaint.token not in tokens:
        tokens.append(complaint.token)

    for t in list(complaint.related_tokens or []):
        if t not in tokens:
            tokens.append(t)

    master.related_tokens = tokens
    master.updated_at = datetime.now(IST)

    complaint.related_tokens = []
    if complaint.severity == "Critical":
        complaint.severity = "Normal"
    master.updated_at = datetime.now(IST)

    dup_update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=current_user_id,
        old_status=old_status,
        new_status="Duplicate",
        note=f"Manually merged into master ticket {master.token}",
    )
    db.add(dup_update)

    escalated = False
    if master.status != "Closed" and master.severity != "Critical":
        master.severity = "Critical"
        escalated = True

    note_text = f"Manually merged with citizen report ({complaint.token})"
    if master.status in ["Closed", "Resolved"]:
        note_text += ". Late duplicate report logged. Due to the 30-day cooldown policy, this issue cannot be re-opened immediately. If you believe this is a mistake, please file a new complaint after the 30-day cooldown period."
    elif escalated:
        note_text += ". Severity escalated to Critical."

    master_update = ComplaintUpdate(
        complaint_id=master.id,
        updated_by_id=current_user_id,
        old_status=master.status,
        new_status=master.status,
        note=note_text,
    )
    db.add(master_update)

    merge_log = AuditLog(
        admin_id=current_user_id,
        action_type="MANUAL_MERGE",
        target_id=complaint.id,
        details=f"Commissioner manually merged ticket {complaint.token} into master {master.token}.",
    )
    db.add(merge_log)

    db.commit()
    return {"message": "Merged successfully"}
