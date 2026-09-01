from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import Facility, FacilityType, User
from application.helpers.schemas import (
    CommissionerFacilityTypeRequest,
    CommissionerFacilityTypeResponse,
)
from application.middlewares.init_jwt import get_current_user_id

router = APIRouter()


@router.put(
    "/commissioner/facility-type/{type_id}", response_model=CommissionerFacilityTypeResponse
)
def update_commissioner_facility_type(
    type_id: int,
    request: CommissionerFacilityTypeRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role("commissioner"):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    if not request.name or not request.name.strip():
        raise HTTPException(status_code=400, detail="Facility type name cannot be empty")

    facility_type = db.query(FacilityType).filter(FacilityType.id == type_id).first()
    if not facility_type:
        raise HTTPException(status_code=404, detail="Facility type not found")

    old_name = facility_type.name
    new_name = request.name.strip()

    if old_name == new_name:
        return {
            "message": "Facility type updated successfully",
            "id": facility_type.id,
            "name": facility_type.name,
        }

    in_use = db.query(Facility).filter(Facility.facility_type == old_name).first()
    if in_use:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit facility type as it is in use by one or more facilities",
        )

    try:
        facility_type.name = new_name
        db.query(Facility).filter(Facility.facility_type == old_name).update(
            {"facility_type": new_name}
        )

        from application.helpers.models import AuditLog

        db.add(
            AuditLog(
                admin_id=current_user_id,
                action_type="COMMISSIONER_UPDATE_FACILITY_TYPE",
                target_id=type_id,
                details=f"Commissioner {user.name} updated facility type to '{new_name}'.",
            )
        )
        db.commit()
        db.refresh(facility_type)
        return {
            "message": "Facility type updated successfully",
            "id": facility_type.id,
            "name": facility_type.name,
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Facility type with this name already exists")
