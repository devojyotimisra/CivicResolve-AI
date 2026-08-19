from typing import List
from application.helpers.schemas import NotificationSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from application.extensions.db_extn import get_db
from application.helpers.models import Notification, User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/notifications", response_model=dict[str, List[NotificationSchema]])
def list_notifications(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    notifs = (
        db.query(Notification)
        .filter(
            or_(
                Notification.user_id == current_user_id,
                Notification.target_role == user.role,
            )
        )
        .order_by(Notification.created_at.desc())
        .all()
    )

    return {"notifications": notifs}
