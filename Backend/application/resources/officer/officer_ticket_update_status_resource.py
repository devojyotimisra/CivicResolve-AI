from application.helpers.schemas import OfficerTicketUpdateStatusRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, ComplaintUpdate, IST
from application.middlewares.init_jwt import get_current_user_id
from application.helpers.notification_helper import create_notification

router = APIRouter()

VALID_TRANSITIONS = {
    'Assigned': ['En Route'],
    'En Route': ['On Site'],
    'On Site': ['In Progress'],
    'In Progress': ['Resolved'],
}


@router.put("/officer/ticket/{complaint_id}/status", response_model=dict[str, str])
def officer_update_ticket_status(
    complaint_id: int,
    data: OfficerTicketUpdateStatusRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('field_officer'):
        raise HTTPException(status_code=403, detail="Officer access required")

    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.assigned_officer_id != current_user_id:
        raise HTTPException(status_code=403, detail="This ticket is not assigned to you")

    new_status = data.status
    if not new_status:
        raise HTTPException(status_code=400, detail="New status is required")

    allowed = VALID_TRANSITIONS.get(complaint.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{complaint.status}' to '{new_status}'"
        )

    old_status = complaint.status
    complaint.status = new_status
    complaint.updated_at = datetime.now(IST)

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=current_user_id,
        old_status=old_status,
        new_status=new_status,
        note=data.note or f"Status updated to {new_status}"
    )

    db.add(update)

    create_notification(
        db,
        target_role="commissioner",
        title="Ticket Status Updated",
        message=f"Complaint #{complaint.token} status changed from {old_status} to {new_status} by {user.name}",
        notif_type="info",
    )

    db.commit()

    return {"message": f"Status updated to {new_status}"}
