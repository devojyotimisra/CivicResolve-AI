from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/complaints")
def commissioner_complaints_list(
    status: str = Query(None),
    department_id: int = Query(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    query = db.query(Complaint)

    if status:
        query = query.filter_by(status=status)
    if department_id:
        query = query.filter_by(department_id=department_id)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    complaints_data = []
    for c in complaints:
        category = db.query(Department).get(c.department_id) if c.department_id else None
        officer = db.query(User).get(c.assigned_officer_id) if c.assigned_officer_id else None
        officer_name_val = officer.name if officer else (c.assigned_officer_name or None)
        complaints_data.append({
            "id": c.id,
            "token": c.token,
            "title": c.title,
            "description": c.description,
            "location": c.location,
            "department": category.name if category else c.department,
            "departmentId": c.department_id,
            "status": c.status,
            "severity": c.severity,
            "assignedOfficer": officer_name_val,
            "assignedOfficerName": officer_name_val,
            "assignedOfficerId": c.assigned_officer_id,
            "createdAt": c.created_at.isoformat() if c.created_at else None,
            "updatedAt": c.updated_at.isoformat() if c.updated_at else None,
        })

    categories = db.query(Department).order_by(Department.name).all()
    categories_data = [{"id": cat.id, "name": cat.name} for cat in categories]

    return {"complaints": complaints_data, "categories": categories_data}
