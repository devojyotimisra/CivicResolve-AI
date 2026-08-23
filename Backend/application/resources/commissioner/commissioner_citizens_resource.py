from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/citizens")
def get_citizens(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    citizens = db.query(User).all()
    citizens = [c for c in citizens if c.has_role("citizen")]

    return {"citizens": [{"id": c.id, "name": c.name, "email": c.email} for c in citizens]}
