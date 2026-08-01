from fastapi import Request
from application.middlewares.init_jwt import create_access_token
from jose import jwt, JWTError
from application.helpers.config import Config


async def refresh_token_middleware(request: Request, call_next):
    response = await call_next(request)

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id:
                new_token = create_access_token(int(user_id))
                response.headers["X-Refresh-Token"] = new_token
        except JWTError:
            pass

    return response
