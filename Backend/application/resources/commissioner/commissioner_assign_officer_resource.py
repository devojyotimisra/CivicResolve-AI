from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import IST, AuditLog, Complaint, ComplaintUpdate, User
from application.helpers.notification_helper import create_notification
from application.helpers.schemas import CommissionerAssignOfficerRequest
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/commissioner/assign/{complaint_id}", response_model=dict[str, str])
def commissioner_assign_officer(
    complaint_id: int,
    data: CommissionerAssignOfficerRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.status == "Closed":
        raise HTTPException(status_code=400, detail="Cannot reassign a closed complaint.")

    if complaint.status == "Duplicate":
        raise HTTPException(
            status_code=400,
            detail="Cannot assign an officer to a Duplicate ticket. Unmerge it first.",
        )

    if complaint.severity != "Critical" and complaint.assigned_officer_id is not None:
        if data.officer_id:
            officer = db.get(User, data.officer_id)
            if officer and officer.department_id == complaint.department_id:
                raise HTTPException(
                    status_code=400,
                    detail="Reassigning officers within the same department is only allowed for Critical complaints.",
                )

    officer_id = data.officer_id
    if not officer_id:
        raise HTTPException(status_code=400, detail="Officer ID is required")

    officer = db.get(User, officer_id)
    if not officer or not officer.has_role("field_officer"):
        raise HTTPException(status_code=400, detail="Invalid officer")

    if not officer.is_active:
        raise HTTPException(status_code=400, detail="Officer account is deactivated")

    if complaint.assigned_officer_id == officer_id:
        raise HTTPException(status_code=400, detail="Officer is already assigned to this ticket")

    old_status = complaint.status
    old_officer_id = complaint.assigned_officer_id

    complaint.assigned_officer_id = officer_id
    complaint.assigned_officer_name = officer.name

    if not complaint.department_id and officer.department_id:
        complaint.department_id = officer.department_id
        complaint.department = officer.department

    if complaint.status in ["Submitted", "Resolved", "Rejected", "Spam"]:
        complaint.status = "Assigned"
        complaint.resolution_note = None

    complaint.updated_at = datetime.now(IST)

    if data.severity:
        if data.severity in ["Low", "Normal", "High", "Critical"]:
            complaint.severity = data.severity

    note_text = f"Complaint assigned to field officer."

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=None,
        old_status=old_status,
        new_status=complaint.status,
        note=note_text,
    )
    db.add(update)

    audit_log = AuditLog(
        admin_id=current_user_id,
        action_type="MANUAL_OFFICER_ASSIGNMENT",
        target_id=complaint.id,
        details=f"Commissioner manually assigned officer: {officer.name} (ID: {officer.id}) to ticket {complaint.token}. Severity: {complaint.severity}",
    )
    db.add(audit_log)

    create_notification(
        db,
        user_id=officer_id,
        title="Ticket Assigned",
        message=f"Assigned to complaint: '{complaint.title}'",
        notif_type="info",
    )

    if old_officer_id and old_officer_id != officer_id:
        create_notification(
            db,
            user_id=old_officer_id,
            title="Ticket Reassigned",
            message=f"'{complaint.title}' was reassigned.",
            notif_type="warning",
        )

    db.commit()

    return {"message": f"Complaint assigned to {officer.name}"}
