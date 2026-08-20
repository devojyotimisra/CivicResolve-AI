from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from application.extensions.db_extn import get_db
from application.helpers.models import Complaint, ComplaintUpdate, Notification, IST
from application.helpers.notification_helper import create_notification

router = APIRouter()

class CitizenResolutionRequest(BaseModel):
    accept: bool
    note: str = None

@router.put("/complaint/track/{token}/resolution", response_model=dict[str, str])
def citizen_respond_resolution(
    token: str,
    data: CitizenResolutionRequest,
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter_by(token=token).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    if complaint.status != 'Resolved':
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot respond to resolution. Current status is '{complaint.status}'"
        )

    old_status = complaint.status
    
    if data.accept:
        new_status = 'Closed'
        complaint.closed_at = datetime.now(IST)
        default_note = "Citizen verified and accepted the resolution photo proof. Case closed."
    else:
        new_status = 'In Progress'
        default_note = "Citizen rejected resolution proof and requested re-opening."
        
        if complaint.assigned_officer_id:
            create_notification(
                db=db,
                user_id=complaint.assigned_officer_id,
                title="Ticket Re-opened",
                message=f"Citizen rejected resolution for complaint #{complaint.token}.",
                notif_type="warning",
            )
        else:
            create_notification(
                db=db,
                target_role="Officer",
                title="Ticket Re-opened",
                message=f"Citizen rejected resolution for complaint #{complaint.token}.",
                notif_type="warning",
            )
            
        create_notification(
            db=db,
            target_role="commissioner",
            title="Ticket Re-opened",
            message=f"Citizen rejected resolution for complaint #{complaint.token}.",
            notif_type="warning",
        )
    complaint.status = new_status
    complaint.updated_at = datetime.now(IST)

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        updated_by_id=None,
        old_status=old_status,
        new_status=new_status,
        note=data.note or default_note
    )

    db.add(update)
    db.commit()

    return {"message": f"Resolution {'accepted' if data.accept else 'rejected'}"}
