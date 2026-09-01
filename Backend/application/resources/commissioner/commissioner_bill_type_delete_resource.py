from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import BillType, User
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.delete("/commissioner/bill_type/{bill_type_id}", response_model=dict[str, str])
def commissioner_delete_bill_type(
    bill_type_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    bill_type = db.get(BillType, bill_type_id)
    if not bill_type:
        raise HTTPException(status_code=404, detail="Bill type not found")

    has_unpaid_bills = any(bill.status.lower() != "paid" for bill in bill_type.bills)
    if has_unpaid_bills:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this bill type because there are unpaid bills associated with it.",
        )

    has_unpaid_bills = any(bill.status.lower() != "paid" for bill in bill_type.bills)
    if has_unpaid_bills:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this bill type because there are unpaid bills associated with it.",
        )

    db.delete(bill_type)
    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="COMMISSIONER_DELETE_BILL_TYPE",
            target_id=bill_type_id,
            details=f"Commissioner {user.name} deleted bill type '{bill_type.name}'.",
        )
    )
    db.commit()

    return {"message": f"Bill type '{bill_type.name}' deleted successfully"}
