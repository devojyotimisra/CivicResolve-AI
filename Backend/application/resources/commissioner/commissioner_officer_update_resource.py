from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/commissioner/officer/{officer_id}")
def commissioner_update_officer(
    officer_id: int,
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    officer = db.query(User).get(officer_id)
    if not officer or not officer.has_role('field_officer'):
        raise HTTPException(status_code=404, detail="Officer not found")

    if data.get("name"):
        officer.name = data["name"].strip()
    if data.get("phone"):
        officer.phone = data["phone"].strip()
    if "active" in data:
        officer.is_active = bool(data["active"])
    if data.get("department"):
        officer.department = data["department"].strip()
    if data.get("jurisdiction_zone"):
        officer.address = data["jurisdiction_zone"].strip()
    # Support badgeId (camelCase) and badge_id (snake_case)
    badge_id = data.get("badgeId") or data.get("badge_id")
    if badge_id is not None:
        officer.badge_id = badge_id.strip() if badge_id else None

    db.commit()

    return {"message": "Officer updated successfully"}
