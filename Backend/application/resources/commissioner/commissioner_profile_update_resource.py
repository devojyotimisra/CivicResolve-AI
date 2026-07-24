from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.extensions.security_extn import hash_password
from application.helpers.models import User
from application.helpers.validators import validate_name, validate_password, validate_phone
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/commissioner/edit_profile")
def commissioner_profile_update(
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        return {"error": "Commissioner access required"}, 403

    if data.get("name"):
        is_valid, result = validate_name(data["name"])
        if not is_valid:
            return {"error": result}, 400
        user.name = result

    if data.get("phone"):
        is_valid, result = validate_phone(data["phone"])
        if not is_valid:
            return {"error": result}, 400
        user.phone = result

    if data.get("password"):
        is_valid, result = validate_password(data["password"])
        if not is_valid:
            return {"error": result}, 400
        user.password = hash_password(result)

    db.commit()

    return {"message": "Profile updated successfully"}
