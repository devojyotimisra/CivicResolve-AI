from application.helpers.schemas import OfficerSearchResponse, CommissionerSearchRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/officer/search", response_model=OfficerSearchResponse)
def officer_search(
    data: CommissionerSearchRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('field_officer'):
        raise HTTPException(status_code=403, detail="Officer access required")

    query_str = (data.query or "").strip()
    if not query_str:
        return {"tickets": []}

    search_term = f"%{query_str}%"

    tickets = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user_id,
        or_(
            Complaint.title.ilike(search_term),
            Complaint.token.ilike(search_term),
            Complaint.location.ilike(search_term),
            Complaint.description.ilike(search_term),
        )
    ).order_by(Complaint.created_at.desc()).all()

    for c in tickets:
        category = db.get(Department, c.department_id) if c.department_id else None
        c.department = category.name if category else c.department

    return {"tickets": tickets}
