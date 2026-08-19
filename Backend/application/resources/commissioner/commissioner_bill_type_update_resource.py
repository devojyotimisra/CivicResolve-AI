from application.helpers.schemas import CommissionerBillTypeRequest, CommissionerBillTypeResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, BillType
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/commissioner/bill_type/{bill_type_id}", response_model=CommissionerBillTypeResponse)
def commissioner_update_bill_type(
    bill_type_id: int,
    data: CommissionerBillTypeRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    bill_type = db.get(BillType, bill_type_id)
    if not bill_type:
        raise HTTPException(status_code=404, detail="Bill type not found")

    name = (data.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Bill type name is required")

    existing = db.query(BillType).filter_by(name=name).first()
    if existing and existing.id != bill_type_id:
        raise HTTPException(status_code=409, detail="Bill type name already in use")

    bill_type.name = name
    db.commit()

    return {"message": "Bill type updated successfully", "id": bill_type.id, "name": bill_type.name}
