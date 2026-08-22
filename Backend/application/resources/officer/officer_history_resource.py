from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Complaint, Department, User
from application.helpers.schemas import OfficerHistoryResponse
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/officer/history", response_model=OfficerHistoryResponse)
def officer_history(
    current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("field_officer"):
        raise HTTPException(status_code=403, detail="Officer access required")

    complaints = (
        db.query(Complaint)
        .filter(Complaint.assigned_officer_id == current_user_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )

    for c in complaints:
        category = db.get(Department, c.department_id) if c.department_id else None
        c.department = category.name if category else c.department

    return {"history": complaints}
