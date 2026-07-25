from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/officer/profile")
def officer_profile_fetch(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('field_officer'):
        raise HTTPException(status_code=403, detail="Officer access required")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "address": user.address,
        "pincode": user.pincode,
        "department": user.department,
        "jurisdiction_zone": user.address,
    }
