from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from application.extensions.db_extn import get_db
from application.helpers.models import Notification, User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


class NotificationCreate(BaseModel):
    title: str
    message: str
    notif_type: str = "info"
    target_user_id: int | None = None
    target_role: str | None = None


def _serialize(n: Notification) -> dict:
    return {
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "notifType": n.notif_type,
        "isRead": n.is_read,
        "createdAt": n.created_at.isoformat() if n.created_at else None,
    }


@router.get("/notifications")
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

    return {"notifications": [_serialize(n) for n in notifs]}


@router.patch("/notifications/{notif_id}/read")
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

    if notif.user_id != current_user_id and notif.target_role != user.role:
        raise HTTPException(status_code=403, detail="Access denied")

    notif.is_read = True
    db.commit()
    return _serialize(notif)


@router.patch("/notifications/{notif_id}/unread")
def mark_as_unread(
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

    if notif.user_id != current_user_id and notif.target_role != user.role:
        raise HTTPException(status_code=403, detail="Access denied")

    notif.is_read = False
    db.commit()
    return _serialize(notif)


@router.patch("/notifications/read-all")
def mark_all_as_read(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(Notification).filter(
        or_(
            Notification.user_id == current_user_id,
            Notification.target_role == user.role,
        ),
        Notification.is_read == False,
    ).update({Notification.is_read: True}, synchronize_session="fetch")
    db.commit()

    return {"message": "All notifications marked as read"}


@router.delete("/notifications/{notif_id}")
def delete_notification(
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

    if notif.user_id != current_user_id and notif.target_role != user.role:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(notif)
    db.commit()
    return {"message": "Notification deleted"}


@router.delete("/notifications")
def clear_all_notifications(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(Notification).filter(
        or_(
            Notification.user_id == current_user_id,
            Notification.target_role == user.role,
        )
    ).delete(synchronize_session="fetch")
    db.commit()

    return {"message": "All notifications cleared"}
