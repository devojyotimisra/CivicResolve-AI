from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import IST, User, UtilityBill
from application.helpers.notification_helper import create_notification
from application.helpers.schemas import CitizenBillPayResponse
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/citizen/pay_bill/{bill_id}", response_model=CitizenBillPayResponse)
def citizen_pay_bill(
    bill_id: int, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("citizen"):
        raise HTTPException(status_code=403, detail="Citizen access required")

    bill = db.get(UtilityBill, bill_id)

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    if bill.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if (bill.status or "").lower() == "paid":
        raise HTTPException(status_code=400, detail="Bill is already paid")

    bill.status = "Paid"
    bill.paid_at = datetime.now(IST)

    import uuid

    payment_ref = f"TXN-{uuid.uuid4().hex[:10].upper()}"
    bill.payment_ref = payment_ref

    create_notification(
        db,
        target_role="commissioner",
        title="Bill Payment Received",
        message=f"{user.name} paid bill {bill.bill_number} ({bill.bill_type}) — ₹{bill.amount:.2f} (Ref: {payment_ref})",
        notif_type="success",
    )
    create_notification(
        db,
        user_id=current_user_id,
        title="Payment Successful",
        message=f"Your payment of ₹{bill.amount:.2f} for {bill.bill_type} ({bill.bill_number}) was successful. Reference: {payment_ref}",
        notif_type="success",
    )

    db.commit()

    return {
        "message": "Payment successful",
        "receipt": {
            "bill_number": bill.bill_number,
            "bill_type": bill.bill_type,
            "amount": bill.amount,
            "paid_at": bill.paid_at.isoformat(),
            "transaction_id": payment_ref,
        },
    }
