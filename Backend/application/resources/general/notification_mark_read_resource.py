from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import Notification, User
from application.middlewares.init_jwt import get_current_user_id
from application.helpers.schemas import NotificationSchema

router = APIRouter()


@router.patch("/notifications/{notif_id}/read", response_model=NotificationSchema)
def mark_as_read(
    notif_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    notif = db.get(Notification, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notif.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif
