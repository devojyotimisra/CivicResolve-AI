from application.helpers.models import Notification


def create_notification(db, *, user_id=None, target_role=None, title, message, notif_type="info"):
    notif = Notification(
        user_id=user_id,
        target_role=target_role,
        title=title,
        message=message,
        notif_type=notif_type,
    )
    db.add(notif)
    return notif
