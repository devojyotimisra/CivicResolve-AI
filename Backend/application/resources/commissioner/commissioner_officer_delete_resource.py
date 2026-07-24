from fastapi import APIRouter, Depends
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
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        return {"error": "Commissioner access required"}, 403

    officer = db.query(User).get(officer_id)
    if not officer or not officer.has_role('field_officer'):
        return {"error": "Officer not found"}, 404

    officer.is_active = False
    db.commit()

    return {"message": "Officer deactivated successfully"}
