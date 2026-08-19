from application.helpers.schemas import CommissionerBillAddRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from application.extensions.db_extn import get_db
from application.helpers.models import User, UtilityBill
from application.helpers.validators import validate_amount
from application.middlewares.init_jwt import get_current_user_id
from application.helpers.notification_helper import create_notification

router = APIRouter()


@router.post("/commissioner/bill", response_model=dict[str, str])
def commissioner_issue_bill(
    data: CommissionerBillAddRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    citizen_id = data.user_id or data.citizen_id
    if not citizen_id:
        raise HTTPException(status_code=400, detail="Citizen ID is required")

    citizen = db.get(User, citizen_id)
    if not citizen or not citizen.has_role('citizen'):
        raise HTTPException(status_code=400, detail="Invalid citizen")

    bill_type = (data.bill_type or "").strip()
    if not bill_type:
        raise HTTPException(status_code=400, detail="Bill type is required")

    is_valid, result = validate_amount(data.amount)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    amount = result

    due_date_str = data.due_date
    if not due_date_str:
        raise HTTPException(status_code=400, detail="Due date is required")

    try:
        due_date = date.fromisoformat(due_date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    period_val = (data.period or "").strip() or None

    import secrets
    bill_number = f"BILL-{secrets.token_urlsafe(6)[:8].upper()}"
    while db.query(UtilityBill).filter_by(bill_number=bill_number).first():
        bill_number = f"BILL-{secrets.token_urlsafe(6)[:8].upper()}"

    bill = UtilityBill(
        user_id=citizen_id,
        citizen_name=citizen.name,
        bill_type=bill_type,
        bill_number=bill_number,
        amount=amount,
        due_date=due_date,
        period=period_val,
        status='Pending'
    )

    db.add(bill)

    create_notification(
        db,
        user_id=citizen_id,
        title="New Bill Issued",
        message=f"A {bill_type} bill of ₹{amount:.2f} ({bill_number}) has been issued to you. Due: {due_date.isoformat()}",
        notif_type="warning",
    )

    db.commit()

    return {"message": f"Bill {bill_number} issued to {citizen.name}"}
