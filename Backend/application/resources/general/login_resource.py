from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.extensions.security_extn import verify_password
from application.helpers.models import User
from application.helpers.validators import validate_password
from application.middlewares.init_jwt import create_access_token
import re

router = APIRouter()


@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    identifier = (data.get("email") or "").strip()
    if not identifier:
        raise HTTPException(status_code=400, detail="Email or Badge ID is required")

    is_valid, result = validate_password(data.get("password"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)

    password = result

    # Determine if identifier is an email or badge ID
    is_email = bool(re.match(r'^[^@ \t\r\n]+@[^@ \t\r\n]+$', identifier))

    if is_email:
        user = db.query(User).filter_by(email=identifier).first()
    else:
        user = db.query(User).filter_by(badge_id=identifier).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account has been deactivated")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(user.id)

    if user.has_role('commissioner'):
        role = 'commissioner'
    elif user.has_role('field_officer'):
        role = 'officer'
    else:
        role = 'citizen'

    return {
        "message": "Login successful",
        "token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": role,
            "badgeId": user.badge_id,
            "phone": user.phone,
            "department": user.department
        }
    }
