import os

from fastapi import APIRouter, Depends, HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from application.extensions.db_extn import get_db
from application.helpers.models import User
from application.helpers.notification_helper import create_notification
from application.helpers.schemas import AuthResponse
from application.middlewares.init_jwt import create_access_token

router = APIRouter()


@router.post("/google-login", response_model=AuthResponse)
def google_login(data: dict, db: Session = Depends(get_db)):
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Google token is required")

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(
            status_code=500, detail="Google Client ID is not configured on the server"
        )

    try:
        if token.startswith("ey"):
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), client_id, clock_skew_in_seconds=10
            )
        else:
            import requests as httprequests

            resp = httprequests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )
            if resp.status_code != 200:
                raise ValueError(f"Invalid access token: {resp.text}")
            idinfo = resp.json()

        email = idinfo.get("email")
        name = idinfo.get("name", "Citizen")

        if not email:
            raise ValueError("Email not provided by Google")

        user = db.query(User).filter_by(email=email).first()

        if not user:
            user = User(
                email=email,
                name=name,
                password="",
                role="citizen",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            create_notification(
                db,
                user_id=user.id,
                title="Complete Your Profile",
                message="Please update your profile with your phone number, address, and pincode to access features like paying bills and booking facilities.",
                notif_type="warning",
            )
            db.commit()
        else:
            if not user.is_active:
                raise HTTPException(status_code=403, detail="Account has been deactivated")

        access_token = create_access_token(user.id)

        if user.has_role("commissioner"):
            role = "commissioner"
        elif user.has_role("field_officer"):
            role = "officer"
        else:
            role = "citizen"
        user.role = role

        return {"message": "Google Login successful", "token": access_token, "user": user}

    except ValueError as e:
        print(f"Google Token Verification Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid Google token")
