from application.helpers.models import Notification, User, Role, user_roles


def create_notification(db, *, user_id=None, target_role=None, title, message, notif_type="info"):
    created_notifs = []
    
    # If a specific user is targeted
    if user_id is not None:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notif_type=notif_type,
        )
        db.add(notif)
        created_notifs.append(notif)
        
    # If a role is targeted (broadcast)
    if target_role is not None:
        # Find all users with this role, either directly or via the many-to-many relationship
        users = db.query(User).filter(
            (User.role == target_role) | (User.roles.any(Role.name == target_role))
        ).all()
        
        for u in users:
            # Don't duplicate if we already added them via user_id
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
            
    # Return the first one for backwards compatibility if callers expect a single object
    return created_notifs[0] if created_notifs else None

