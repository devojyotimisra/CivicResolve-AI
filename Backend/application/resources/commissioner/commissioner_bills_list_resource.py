from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import User, UtilityBill
from application.helpers.schemas import UtilityBillSchema
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/bills", response_model=dict[str, List[UtilityBillSchema]])
def commissioner_bills_list(
    current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    bills = db.query(UtilityBill).order_by(UtilityBill.created_at.desc()).all()

    return {"bills": bills}
