from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.helpers.models import User, UtilityBill
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.get("/commissioner/bills")
def commissioner_bills_list(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    bills = db.query(UtilityBill).order_by(UtilityBill.created_at.desc()).all()

    bills_data = []
    for bill in bills:
        citizen = db.get(User, bill.user_id) if bill.user_id else None
        citizen_name_val = citizen.name if citizen else (bill.citizen_name or "N/A")
        due_date_str = bill.due_date.isoformat() if bill.due_date else None
        paid_at_str = bill.paid_at.isoformat() if bill.paid_at else None
        created_at_str = bill.created_at.isoformat() if bill.created_at else None

        bills_data.append({
            "id": bill.id,
            "billType": bill.bill_type,
            "billNumber": bill.bill_number,
            "amount": bill.amount,
            "dueDate": due_date_str,
            "period": bill.period,
            "status": bill.status,
            "citizenName": citizen_name_val,
            "citizenId": bill.user_id,
            "paidAt": paid_at_str,
            "createdAt": created_at_str,
        })

    return {"bills": bills_data}
