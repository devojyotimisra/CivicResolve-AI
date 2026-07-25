from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, BillType
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()

@router.get("/commissioner/bill_types")
def commissioner_bill_types_list(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).get(current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    bill_types = db.query(BillType).order_by(BillType.name.asc()).all()

    bill_types_data = []
    for b in bill_types:
        bill_types_data.append({
            "id": b.id,
            "name": b.name,
        })

    return bill_types_data
