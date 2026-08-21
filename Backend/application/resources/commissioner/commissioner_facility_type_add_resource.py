from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from application.extensions.db_extn import get_db
from application.middlewares.init_jwt import get_current_user_id
from application.helpers.models import FacilityType, User
from application.helpers.schemas import CommissionerFacilityTypeRequest, CommissionerFacilityTypeResponse

router = APIRouter()

@router.post("/commissioner/facility-type", response_model=CommissionerFacilityTypeResponse)
def add_commissioner_facility_type(
    request: CommissionerFacilityTypeRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, current_user_id)
    if not user or not user.has_role('commissioner'):
        raise HTTPException(status_code=403, detail="Commissioner access required")

    if not request.name or not request.name.strip():
        raise HTTPException(status_code=400, detail="Facility type name cannot be empty")
    
    try:
        new_type = FacilityType(name=request.name.strip())
        db.add(new_type)
        db.commit()
        db.refresh(new_type)
        return {"message": "Facility type added successfully", "id": new_type.id, "name": new_type.name}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Facility type with this name already exists")
