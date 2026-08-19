from typing import List
from application.helpers.schemas import ComplaintSchema, DepartmentSchema
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/complaints", response_model=dict[str, List[ComplaintSchema] | List[DepartmentSchema]])
def commissioner_complaints_list(
    status: str = Query(None),
    department_id: int = Query(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    query = db.query(Complaint)

    if status:
        query = query.filter_by(status=status)
    if department_id:
        query = query.filter_by(department_id=department_id)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    for c in complaints:
        category = db.get(Department, c.department_id) if c.department_id else None
        officer = db.get(User, c.assigned_officer_id) if c.assigned_officer_id else None
        c.department = category.name if category else c.department
        c.assigned_officer_name = officer.name if officer else (c.assigned_officer_name or None)

    categories = db.query(Department).order_by(Department.name).all()

    return {"complaints": complaints, "categories": categories}
