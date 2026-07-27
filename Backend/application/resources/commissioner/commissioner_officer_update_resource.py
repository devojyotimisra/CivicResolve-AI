from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Department
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

    dept_input = data.get("department") or data.get("department_id")
    if dept_input is not None and str(dept_input).strip():
        dept_raw = str(dept_input).strip()
        dept_obj = None
        if dept_raw.isdigit():
            dept_obj = db.query(Department).get(int(dept_raw))
        if not dept_obj:
            dept_obj = db.query(Department).filter_by(name=dept_raw).first()

        if not dept_obj:
            raise HTTPException(status_code=400, detail="Invalid department")

        officer.department_id = dept_obj.id
        officer.department = dept_obj.name

    if data.get("jurisdiction_zone"):
        officer.address = data["jurisdiction_zone"].strip()
    # Support badgeId (camelCase) and badge_id (snake_case)
    badge_id = data.get("badgeId") or data.get("badge_id")
    if badge_id is not None:
        officer.badge_id = badge_id.strip() if badge_id else None

    db.commit()

    return {"message": "Officer updated successfully"}
