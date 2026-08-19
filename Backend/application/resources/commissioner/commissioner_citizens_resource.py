from typing import List
from application.helpers.schemas import UserSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/citizens", response_model=dict[str, List[UserSchema]])
def commissioner_citizens_list(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    citizens = db.query(User).filter(
        or_(User.role == 'citizen', User.roles.any(name='citizen'))
    ).order_by(User.name.asc()).all()
    return {"citizens": citizens}
