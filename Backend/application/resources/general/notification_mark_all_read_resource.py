from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Notification, User
from application.helpers.schemas import MessageResponse
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.patch("/notifications/read-all", response_model=MessageResponse)
def mark_all_as_read(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(Notification).filter(
        Notification.user_id == current_user_id,
        ~Notification.is_read,
    ).update({Notification.is_read: True}, synchronize_session="fetch")

    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="USER_MARK_ALL_NOTIFICATIONS_READ",
            target_id=current_user_id,
            details=f"User {user.name} marked all notifications as read.",
        )
    )
    db.commit()

    return {"message": "All notifications marked as read"}
