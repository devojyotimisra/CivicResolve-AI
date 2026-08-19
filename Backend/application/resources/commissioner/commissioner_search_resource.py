from typing import List
from application.helpers.schemas import CommissionerSearchRequest, ComplaintSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/search", response_model=dict[str, List[ComplaintSchema]])
def commissioner_search(
    data: CommissionerSearchRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    query_str = (data.query or "").strip()
    if not query_str:
        return {"complaints": []}

    search_term = f"%{query_str}%"

    complaints = db.query(Complaint).filter(
        or_(
            Complaint.title.ilike(search_term),
            Complaint.token.ilike(search_term),
            Complaint.location.ilike(search_term),
            Complaint.description.ilike(search_term),
        )
    ).order_by(Complaint.created_at.desc()).all()

    for c in complaints:
        category = db.get(Department, c.department_id) if c.department_id else None
        officer = db.get(User, c.assigned_officer_id) if c.assigned_officer_id else None
        c.department = category.name if category else c.department
        c.assigned_officer_name = officer.name if officer else None

    return {"complaints": complaints}
