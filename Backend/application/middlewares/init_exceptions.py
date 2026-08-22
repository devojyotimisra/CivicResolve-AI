from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def init_exceptions(app: FastAPI):
    @app.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
        error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        if "phone" in error_msg.lower():
            detail = "This phone number is already registered."
        elif "email" in error_msg.lower():
            detail = "This email is already registered."
        elif "badge_id" in error_msg.lower():
            detail = "This badge ID is already registered."
        else:
            detail = "A duplicate record was found."

        return JSONResponse(status_code=409, content={"detail": detail})
