from application.extensions.db_extn import Base, init_engine
from application.extensions.security_extn import hash_password
from application.helpers.models import Role, User


def initialize_database(app):
    config = app.state.config
    init_engine(config.SQLALCHEMY_DATABASE_URI)

    from application.extensions.db_extn import SessionLocal, engine

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if not db.query(Role).first():
            citizen_role = Role(name="citizen")
            officer_role = Role(name="field_officer")
            commissioner_role = Role(name="commissioner")
            db.add_all([citizen_role, officer_role, commissioner_role])
            db.commit()

        existing_commissioner = db.query(User).filter_by(email=config.COMMISSIONER_MAIL).first()
        if not existing_commissioner:
            commissioner = User(
                email=config.COMMISSIONER_MAIL,
                password=hash_password(config.COMMISSIONER_PASSWORD),
                name=config.COMMISSIONER_NAME,
                role="commissioner",
                badge_id="COM-001",
                is_active=True,
            )

            commissioner_role = db.query(Role).filter_by(name="commissioner").first()
            commissioner.roles.append(commissioner_role)

            db.add(commissioner)
            db.commit()
            db.refresh(commissioner)

            from application.helpers.notification_helper import create_notification

            create_notification(
                db=db,
                user_id=commissioner.id,
                title="Update Profile",
                message="Please update your profile in accordance",
                notif_type="warning",
            )
            db.commit()
        else:
            updated = False
            if not existing_commissioner.badge_id:
                existing_commissioner.badge_id = "COM-001"
                updated = True
            if existing_commissioner.role != "commissioner":
                existing_commissioner.role = "commissioner"
                updated = True
            if updated:
                db.commit()

    finally:
        db.close()
