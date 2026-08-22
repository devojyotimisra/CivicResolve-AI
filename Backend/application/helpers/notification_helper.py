from application.helpers.models import Notification, Role, User


def create_notification(db, *, user_id=None, target_role=None, title, message, notif_type="info"):
    created_notifs = []

    if user_id is not None:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notif_type=notif_type,
        )
        db.add(notif)
        created_notifs.append(notif)

    if target_role is not None:
        users = (
            db.query(User)
            .filter((User.role == target_role) | (User.roles.any(Role.name == target_role)))
            .all()
        )

        for u in users:
            if u.id == user_id:
                continue

            notif = Notification(
                user_id=u.id,
                title=title,
                message=message,
                notif_type=notif_type,
            )
            db.add(notif)
            created_notifs.append(notif)

    return created_notifs[0] if created_notifs else None
