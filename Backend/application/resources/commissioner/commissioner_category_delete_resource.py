from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, Department
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.delete("/commissioner/category/{category_id}")
def commissioner_delete_category(
    category_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        return {"error": "Commissioner access required"}, 403

    category = db.query(Department).get(category_id)
    if not category:
        return {"error": "Category not found"}, 404

    db.delete(category)
    db.commit()

    return {"message": "Category deleted"}
