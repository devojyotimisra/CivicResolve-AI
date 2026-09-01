from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import BillType, User
from application.helpers.schemas import CommissionerBillTypeRequest, CommissionerBillTypeResponse
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/bill_type", response_model=CommissionerBillTypeResponse)
def commissioner_create_bill_type(
    data: CommissionerBillTypeRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    name = (data.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Bill type name is required")

    if db.query(BillType).filter_by(name=name).first():
        raise HTTPException(status_code=409, detail="Bill type already exists")

    bill_type = BillType(name=name)
    db.add(bill_type)
    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="COMMISSIONER_ADD_BILL_TYPE",
            target_id=None,
            details=f"Commissioner {user.name} created bill type '{name}'.",
        )
    )
    db.commit()
    db.refresh(bill_type)

    return {
        "message": f"Bill type '{name}' created successfully",
        "id": bill_type.id,
        "name": bill_type.name,
    }
