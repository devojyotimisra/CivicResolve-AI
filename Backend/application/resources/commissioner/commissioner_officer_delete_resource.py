from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.delete("/commissioner/officer/{officer_id}")
def commissioner_delete_officer(
    officer_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    officer = db.get(User, officer_id)
    if not officer or not officer.has_role('field_officer'):
        raise HTTPException(status_code=404, detail="Officer not found")

    officer.is_active = False
    db.commit()

    return {"message": "Officer deactivated successfully"}
