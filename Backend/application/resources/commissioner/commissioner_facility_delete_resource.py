from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Facility
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()

@router.delete("/commissioner/facility/{facility_id}")
def commissioner_delete_facility(
    facility_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        return {"error": "Commissioner access required"}, 403

    facility = db.query(Facility).get(facility_id)
    if not facility:
        return {"error": "Facility not found"}, 404

    facility.is_active = False
    db.commit()

    return {"message": "Facility deactivated"}
