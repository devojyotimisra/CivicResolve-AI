from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role
from application.helpers.validators import validate_email, validate_name
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/officer")
def commissioner_add_officer(
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    is_valid, result = validate_email(data.get("email"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    email = result

    is_valid, result = validate_name(data.get("name"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    name = result

    # badge_id: frontend sends as "badgeId"
    badge_id = (data.get("badgeId") or data.get("badge_id") or "").strip() or None

    department = (data.get("department") or "").strip()
    if not department:
        raise HTTPException(status_code=400, detail="Department is required")

    # jurisdiction_zone: optional, frontend does not send it
    jurisdiction_zone = (data.get("jurisdiction_zone") or "").strip()

    # password: optional — frontend does not send it; default to badge_id
    password_raw = (data.get("password") or "").strip()
    if not password_raw:
        password_raw = badge_id if badge_id else "officer123"

    if db.query(User).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    if badge_id and db.query(User).filter_by(badge_id=badge_id).first():
        raise HTTPException(status_code=409, detail="Badge ID already in use")

    officer_role = db.query(Role).filter_by(name='field_officer').first()

    new_officer = User(
        email=email,
        password=hash_password(password_raw),
        name=name,
        phone=data.get("phone"),
        address=data.get("address") or jurisdiction_zone or department,
        pincode=data.get("pincode"),
        department=department,
        badge_id=badge_id,
        role='field_officer',
        is_active=True
    )
    new_officer.roles.append(officer_role)
    db.add(new_officer)
    db.commit()

    return {"message": f"Officer {name} created successfully"}
