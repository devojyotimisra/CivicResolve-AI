from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Complaint, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/citizen/complaints")
def citizen_complaints_list(
    status: str = Query(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('citizen'):
        return {"error": "Citizen access required"}, 403

    query = db.query(Complaint).filter_by(user_id=current_user_id)

    if status:
        query = query.filter_by(status=status)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    complaints_data = []
    for c in complaints:
        category = db.query(Department).get(c.department_id) if c.department_id else None
        complaints_data.append({
            "id": c.id,
            "tracking_token": c.tracking_token,
            "title": c.title,
            "category": category.name if category else None,
            "status": c.status,
            "priority": c.priority,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        })

    return {"complaints": complaints_data}
