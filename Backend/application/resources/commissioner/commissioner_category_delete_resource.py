from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.delete("/commissioner/category/{category_id}", response_model=dict[str, str])
def commissioner_delete_category(
    category_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    category = db.get(Department, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()

    return {"message": "Category deleted"}
