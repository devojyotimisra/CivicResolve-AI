import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.extensions.security_extn import verify_password
from application.helpers.models import User
from application.helpers.schemas import AuthResponse
from application.middlewares.init_jwt import create_access_token

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(data: dict, db: Session = Depends(get_db)):
    identifier = (data.get("email") or "").strip()
    if not identifier:
        raise HTTPException(status_code=400, detail="Email or Badge ID is required")

    password = (data.get("password") or "").strip()
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    is_email = bool(re.match(r"^[^@ \t\r\n]+@[^@ \t\r\n]+$", identifier))

    if is_email:
        user = db.query(User).filter_by(email=identifier).first()
    else:
        user = db.query(User).filter_by(badge_id=identifier).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account has been deactivated")

    if not user.password:
        raise HTTPException(
            status_code=400, detail="This account uses Google Login. Please sign in with Google."
        )

    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(user.id)

    if user.has_role("commissioner"):
        role = "commissioner"
    elif user.has_role("field_officer"):
        role = "officer"
    else:
        role = "citizen"

    user.role = role

    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=user.id,
            action_type="AUTH_LOGIN",
            target_id=user.id,
            details=f"User {user.name} logged in.",
        )
    )
    db.commit()

    return {"message": "Login successful", "token": access_token, "user": user}
