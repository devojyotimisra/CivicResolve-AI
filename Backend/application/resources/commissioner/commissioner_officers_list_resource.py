from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from application.extensions.db_extn import get_db
from application.helpers.models import Complaint, User
from application.helpers.schemas import UserSchema
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/officers", response_model=dict[str, List[UserSchema]])
def commissioner_officers_list(
    current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    officers = (
        db.query(User)
        .options(joinedload(User.department_rel))
        .filter(or_(User.role == "field_officer", User.roles.any(name="field_officer")))
        .order_by(User.name.asc())
        .all()
    )

    result = []
    for o in officers:
        active_count = (
            db.query(Complaint)
            .filter(
                Complaint.assigned_officer_id == o.id,
                Complaint.status.in_(["Assigned", "En Route", "On Site", "In Progress"]),
            )
            .count()
        )

        officer_dict = {
            "id": o.id,
            "email": o.email,
            "name": o.name,
            "role": o.role,
            "badge_id": o.badge_id,
            "department_id": o.department_id,
            "department": o.department,
            "phone": o.phone,
            "address": o.address,
            "pincode": o.pincode,
            "is_active": o.is_active,
            "active": o.is_active,
        }
        result.append(UserSchema.model_validate(officer_dict))

    return {"officers": result}
