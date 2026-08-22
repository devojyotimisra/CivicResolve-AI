from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import User, UtilityBill
from application.helpers.schemas import UtilityBillSchema
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/citizen/bills", response_model=dict[str, List[UtilityBillSchema]])
def citizen_bills_list(
    status: str = Query(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("citizen"):
        raise HTTPException(status_code=403, detail="Citizen access required")

    query = db.query(UtilityBill).filter_by(user_id=current_user_id)

    if status:
        query = query.filter_by(status=status)

    bills = query.order_by(UtilityBill.due_date.desc()).all()

    bills = query.order_by(UtilityBill.due_date.desc()).all()
    return {"bills": bills}
