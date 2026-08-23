from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Department, User
from application.helpers.schemas import CommissionerCategoryAddRequest
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/category", response_model=dict[str, str])
def commissioner_add_category(
    data: CommissionerCategoryAddRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    name = (data.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Department name is required")

    category_id = data.id

    existing = db.query(Department).filter_by(name=name).first()

    if category_id:
        if existing and existing.id != int(category_id):
            raise HTTPException(status_code=409, detail="Department already exists")

        category = db.get(Department, int(category_id))
        if not category:
            raise HTTPException(status_code=404, detail="Department not found")

        if category.users_in_dept:
            raise HTTPException(
                status_code=400,
                detail="Cannot edit department. There are officers present in this department.",
            )

        category.name = name
        db.commit()
        return {"message": f"Department '{name}' updated successfully"}
    else:
        if existing:
            raise HTTPException(status_code=409, detail="Department already exists")

        category = Department(name=name)
        db.add(category)
        db.commit()
        return {"message": f"Department '{name}' created successfully"}
