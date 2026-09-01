from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.extensions.security_extn import hash_password, verify_password
from application.helpers.models import User
from application.helpers.schemas import PasswordUpdateRequest
from application.helpers.validators import validate_password
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put("/update_password", response_model=dict[str, str])
def update_password(
    data: PasswordUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.current_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    is_valid, result = validate_password(data.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)

    user.password = hash_password(result)
    from application.helpers.models import AuditLog

    db.add(
        AuditLog(
            admin_id=current_user_id,
            action_type="USER_UPDATE_PASSWORD",
            target_id=current_user_id,
            details=f"User {user.name} updated their password.",
        )
    )
    db.commit()

    return {"message": "Password updated successfully!"}
