from application.helpers.schemas import CommissionerOfficerUpdateRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/commissioner/officer/{officer_id}", response_model=dict[str, str])
def commissioner_update_officer(
    officer_id: int,
    data: CommissionerOfficerUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    officer = db.get(User, officer_id)
    if not officer or not officer.has_role('field_officer'):
        raise HTTPException(status_code=404, detail="Officer not found")

    if data.name:
        officer.name = data.name.strip()
    if data.phone:
        officer.phone = data.phone.strip()
    if data.active is not None:
        officer.is_active = data.active

    dept_input = data.department or data.department_id
    if dept_input is not None and str(dept_input).strip():
        dept_raw = str(dept_input).strip()
        dept_obj = None
        if dept_raw.isdigit():
            dept_obj = db.get(Department, int(dept_raw))
        if not dept_obj:
            dept_obj = db.query(Department).filter_by(name=dept_raw).first()

        if not dept_obj:
            raise HTTPException(status_code=400, detail="Invalid department")

        officer.department_id = dept_obj.id

    if data.jurisdiction_zone:
        officer.address = data.jurisdiction_zone.strip()
    badge_id = data.badge_id
    if badge_id is not None:
        officer.badge_id = badge_id.strip() if badge_id else None

    db.commit()

    return {"message": "Officer updated successfully"}
