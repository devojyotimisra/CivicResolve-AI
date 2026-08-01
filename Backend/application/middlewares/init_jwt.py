from datetime import datetime, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from application.helpers.config import Config


security = HTTPBearer()


def create_access_token(user_id: int):
    expires = datetime.now(timezone.utc) + Config.JWT_ACCESS_TOKEN_EXPIRES
    payload = {
        "sub": str(user_id),
        "exp": expires
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
