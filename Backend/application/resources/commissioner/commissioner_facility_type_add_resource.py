from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import FacilityType, User
from application.helpers.schemas import (
    CommissionerFacilityTypeRequest,
    CommissionerFacilityTypeResponse,
)
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.post("/commissioner/facility-type", response_model=CommissionerFacilityTypeResponse)
def add_commissioner_facility_type(
    request: CommissionerFacilityTypeRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    if not request.name or not request.name.strip():
        raise HTTPException(status_code=400, detail="Facility type name cannot be empty")

    try:
        new_type = FacilityType(name=request.name.strip())
        db.add(new_type)
        from application.helpers.models import AuditLog

        db.add(
            AuditLog(
                admin_id=current_user_id,
                action_type="COMMISSIONER_ADD_FACILITY_TYPE",
                target_id=None,
                details=f"Commissioner {user.name} created facility type '{request.name.strip()}'.",
            )
        )
        db.commit()
        db.refresh(new_type)
        return {
            "message": "Facility type added successfully",
            "id": new_type.id,
            "name": new_type.name,
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Facility type with this name already exists")
