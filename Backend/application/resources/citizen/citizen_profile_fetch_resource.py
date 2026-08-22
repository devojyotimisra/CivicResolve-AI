from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.helpers.schemas import UserSchema
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/citizen/profile", response_model=UserSchema)
def citizen_profile_fetch(
    current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("citizen"):
        raise HTTPException(status_code=403, detail="Citizen access required")

    return user
