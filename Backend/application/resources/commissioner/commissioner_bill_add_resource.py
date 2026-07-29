from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from application.extensions.db_extn import get_db
from application.helpers.models import User, UtilityBill
from application.helpers.validators import validate_amount
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/bill")
def commissioner_issue_bill(
    data: dict,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    # Accept userId (sent by Bills.jsx), citizenId (camelCase), or citizen_id (snake_case)
    citizen_id = data.get("userId") or data.get("citizenId") or data.get("citizen_id")
    if not citizen_id:
        raise HTTPException(status_code=400, detail="Citizen ID is required")

    citizen = db.get(User, citizen_id)
    if not citizen or not citizen.has_role('citizen'):
        raise HTTPException(status_code=400, detail="Invalid citizen")

    # Accept both camelCase (billType) and snake_case (bill_type)
    bill_type = (data.get("billType") or data.get("bill_type", "")).strip()
    if not bill_type:
        raise HTTPException(status_code=400, detail="Bill type is required")

    is_valid, result = validate_amount(data.get("amount"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    amount = result

    # Accept both camelCase (dueDate) and snake_case (due_date)
    due_date_str = data.get("dueDate") or data.get("due_date")
    if not due_date_str:
        raise HTTPException(status_code=400, detail="Due date is required")

    try:
        due_date = date.fromisoformat(due_date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    period_val = (data.get("period") or "").strip() or None

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
        status='Pending'  # Title Case matching DB default
    )

    db.add(bill)
    db.commit()

    return {"message": f"Bill {bill_number} issued to {citizen.name}"}
