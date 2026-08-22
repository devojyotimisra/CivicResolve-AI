from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.extensions.security_extn import hash_password
from application.helpers.models import Department, Role, User
from application.helpers.schemas import CommissionerOfficerAddRequest
from application.helpers.validators import validate_email, validate_name, validate_password
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/officer", response_model=dict[str, str])
def commissioner_add_officer(
    data: CommissionerOfficerAddRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    is_valid, result = validate_email(data.email)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    email = result

    is_valid, result = validate_name(data.name)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    name = result

    badge_id = (data.badge_id or "").strip() or None

    dept_obj = None
    if data.department_id:
        dept_obj = db.get(Department, data.department_id)
    if not dept_obj and data.department:
        department_raw = str(data.department).strip()
        if department_raw.isdigit():
            dept_obj = db.get(Department, int(department_raw))
        if not dept_obj:
            dept_obj = db.query(Department).filter_by(name=department_raw).first()

    if not data.department_id and not data.department:
        raise HTTPException(status_code=400, detail="Department is required")

    if not dept_obj:
        raise HTTPException(status_code=400, detail="Invalid department")

    jurisdiction_zone = (data.jurisdiction_zone or "").strip()

    password_raw = (data.password or "").strip()
    if not password_raw:
        password_raw = "Officer@123"

    is_valid, result = validate_password(password_raw)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    password_raw = result

    if db.query(User).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    if badge_id and db.query(User).filter_by(badge_id=badge_id).first():
        raise HTTPException(status_code=409, detail="Badge ID already in use")

    officer_role = db.query(Role).filter_by(name="field_officer").first()

    new_officer = User(
        email=email,
        password=hash_password(password_raw),
        name=name,
        phone=data.phone,
        address=data.address or jurisdiction_zone or dept_obj.name,
        pincode=data.pincode,
        department_id=dept_obj.id,
        badge_id=badge_id,
        role="field_officer",
        is_active=True,
    )
    new_officer.roles.append(officer_role)
    db.add(new_officer)
    db.commit()
    db.refresh(new_officer)

    from application.helpers.notification_helper import create_notification

    create_notification(
        db=db,
        user_id=new_officer.id,
        title="Welcome to the Platform!",
        message="You have been added as a Field Officer. Please update your profile and password.",
        notif_type="info",
    )
    db.commit()

    return {"message": f"Officer {name} created successfully"}
