from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.extensions.security_extn import hash_password
from application.helpers.models import User
from application.helpers.validators import validate_name, validate_password, validate_phone
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/profile")
def commissioner_profile_fetch(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        return {"error": "Commissioner access required"}, 403

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "address": user.address,
        "pincode": user.pincode,
    }

