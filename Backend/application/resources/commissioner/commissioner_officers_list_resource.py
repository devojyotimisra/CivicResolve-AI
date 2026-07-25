from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/officers")
def commissioner_officers_list(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    officers = db.query(User).filter(
        or_(User.role == 'field_officer', User.roles.any(name='field_officer'))
    ).order_by(User.name.asc()).all()

    officers_data = []
    for o in officers:
        created_at_val = getattr(o, 'created_at', None)
        created_at_str = created_at_val.isoformat() if created_at_val and hasattr(created_at_val, 'isoformat') else None
        officers_data.append({
            "id": o.id,
            "email": o.email,
            "name": o.name,
            "phone": o.phone,
            "badgeId": o.badge_id,
            "active": o.is_active,
            "department": o.department,
            "jurisdictionZone": o.address,
            "createdAt": created_at_str,
        })

    return {"officers": officers_data}
