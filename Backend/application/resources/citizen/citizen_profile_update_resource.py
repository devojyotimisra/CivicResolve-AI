from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.helpers.schemas import CitizenProfileUpdateRequest
from application.helpers.validators import (
    validate_address,
    validate_email,
    validate_name,
    validate_phone,
    validate_pincode,
)
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/citizen/edit_profile", response_model=dict[str, str])
def citizen_profile_update(
    data: CitizenProfileUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("citizen"):
        raise HTTPException(status_code=403, detail="Citizen access required")

    if data.email:
        is_valid, result = validate_email(data.email)
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        existing = db.query(User).filter_by(email=result).first()
        if existing and existing.id != current_user_id:
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = result

    if data.name:
        is_valid, result = validate_name(data.name)
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        user.name = result

    if data.address:
        is_valid, result = validate_address(data.address)
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        user.address = result

    if data.pincode:
        is_valid, result = validate_pincode(data.pincode)
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        user.pincode = result

    if data.phone:
        is_valid, result = validate_phone(data.phone)
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        user.phone = result

    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="CITIZEN_UPDATE_PROFILE",
            target_id=user.id,
            details=f"Citizen {user.name} updated their profile.",
        )
    )
    db.commit()

    return {"message": "Profile updated successfully"}
