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


def generate_due_date_notifications(db, user_id: int):
    from datetime import date, timedelta

    from application.helpers.models import Notification, UtilityBill

    today = date.today()
    target_date = today + timedelta(days=15)

    bills = (
        db.query(UtilityBill)
        .filter(
            UtilityBill.user_id == user_id,
            UtilityBill.status == "Pending",
            UtilityBill.due_date >= today,
            UtilityBill.due_date <= target_date,
        )
        .all()
    )

    for bill in bills:
        days_left = (bill.due_date - today).days
        time_text = (
            "today" if days_left == 0 else f"in {days_left} day{'s' if days_left > 1 else ''}"
        )
        msg = f"Your {bill.bill_type} bill (₹{bill.amount:.2f}) is due {time_text}."

        tracker_msg = f"U{user_id}_{msg}"
        exists = (
            db.query(Notification)
            .filter(
                Notification.user_id.is_(None),
                Notification.title == "SYS_TRACKER",
                Notification.message == tracker_msg,
            )
            .first()
        )

        if not exists:
            tracker = Notification(
                user_id=None, title="SYS_TRACKER", message=tracker_msg, notif_type="hidden"
            )
            db.add(tracker)

            notif = Notification(
                user_id=user_id, title="Bill Due Reminder", message=msg, notif_type="warning"
            )
            db.add(notif)
    db.commit()


def apply_overdue_fines(db, user_id: int):
    from datetime import date

    from application.helpers.models import Notification, UtilityBill

    today = date.today()

    overdue_bills = (
        db.query(UtilityBill)
        .filter(
            UtilityBill.user_id == user_id,
            UtilityBill.status.in_(["Pending", "Overdue"]),
            UtilityBill.due_date < today,
        )
        .all()
    )

    for bill in overdue_bills:
        days_overdue = (today - bill.due_date).days

        fines_applied_count = (
            db.query(Notification)
            .filter(
                Notification.user_id.is_(None),
                Notification.title == "SYS_TRACKER",
                Notification.message.like(f"FINE_{bill.id}_%"),
            )
            .count()
        )

        missing_fines = days_overdue - fines_applied_count

        if missing_fines > 0:
            previous_amount = bill.amount
            added_fine = missing_fines * 50.0
            bill.amount += added_fine
            bill.status = "Overdue"

            for i in range(missing_fines):
                tracker_msg = f"FINE_{bill.id}_{fines_applied_count + i + 1}"
                tracker = Notification(
                    user_id=None, title="SYS_TRACKER", message=tracker_msg, notif_type="hidden"
                )
                db.add(tracker)

            msg = f"Your {bill.bill_type} bill is overdue! ₹{added_fine:.0f} in fines added. New amount: ₹{bill.amount:.2f} (was ₹{previous_amount:.2f})."
            notif = Notification(
                user_id=user_id, title="Overdue Bill Fine", message=msg, notif_type="error"
            )
            db.add(notif)

    db.commit()
