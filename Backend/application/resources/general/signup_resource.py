from application.helpers.schemas import AuthResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from application.extensions.db_extn import get_db
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role
from application.helpers.validators import validate_email, validate_password, validate_name, validate_address, validate_pincode, validate_phone
from application.middlewares.init_jwt import create_access_token

router = APIRouter()


@router.post("/signup", response_model=AuthResponse)
def signup(data: dict, db: Session = Depends(get_db)):
    is_valid, result = validate_email(data.get("email"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    email = result

    is_valid, result = validate_password(data.get("password"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    password = result

    is_valid, result = validate_name(data.get("name"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    name = result

    is_valid, result = validate_address(data.get("address"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    address = result

    is_valid, result = validate_pincode(data.get("pincode"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    pincode = result

    is_valid, result = validate_phone(data.get("phone"))
    if not is_valid:
        raise HTTPException(status_code=400, detail=result)
    phone = result

    if db.query(User).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = hash_password(password)

    citizen_role = db.query(Role).filter_by(name='citizen').first()
    if not citizen_role:
        citizen_role = Role(name='citizen')
        db.add(citizen_role)
        db.commit()

    new_user = User(
        email=email,
        password=hashed_password,
        name=name,
        address=address,
        pincode=pincode,
        phone=phone
    )

    new_user.roles.append(citizen_role)

    db.add(new_user)
    db.commit()

    access_token = create_access_token(new_user.id)
    new_user.role = "citizen"

    return {
        "message": "Account created successfully",
        "token": access_token,
        "user": new_user
    }
