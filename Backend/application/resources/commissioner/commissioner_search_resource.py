from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/search")
def commissioner_search(
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    query_str = data.get("query", "").strip()
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

    complaints_data = []
    for c in complaints:
        category = db.query(Department).get(c.department_id) if c.department_id else None
        officer = db.query(User).get(c.assigned_officer_id) if c.assigned_officer_id else None
        complaints_data.append({
            "id": c.id,
            "token": c.token,
            "title": c.title,
            "description": c.description,
            "department": category.name if category else c.department,
            "location": c.location,
            "status": c.status,
            "severity": c.severity,
            "assignedOfficer": officer.name if officer else None,
            "createdAt": c.created_at.isoformat() if c.created_at else None,
        })

    return {"complaints": complaints_data}
