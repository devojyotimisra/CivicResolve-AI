from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.extensions.security_extn import hash_password
from application.helpers.models import User
from application.helpers.validators import validate_name, validate_password, validate_phone
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/officer/edit_profile")
def officer_profile_update(
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('field_officer'):
        raise HTTPException(status_code=403, detail="Officer access required")

    if data.get("name"):
        is_valid, result = validate_name(data["name"])
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        user.name = result

    if data.get("phone"):
        is_valid, result = validate_phone(data["phone"])
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        user.phone = result

    if data.get("password"):
        is_valid, result = validate_password(data["password"])
        if not is_valid:
            raise HTTPException(status_code=400, detail=result)
        user.password = hash_password(result)

    db.commit()

    return {"message": "Profile updated successfully"}
