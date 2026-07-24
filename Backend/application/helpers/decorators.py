from functools import wraps
from fastapi import HTTPException
from application.helpers.models import User


def citizen_required(fn):
    @wraps(fn)
    def wrapper(*args, current_user_id: int = None, db=None, **kwargs):
        user = db.query(User).get(current_user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.has_role('citizen'):
            raise HTTPException(status_code=403, detail="Citizen access required")

        return fn(*args, current_user_id=current_user_id, db=db, **kwargs)
    return wrapper


def officer_required(fn):
    @wraps(fn)
    def wrapper(*args, current_user_id: int = None, db=None, **kwargs):
        user = db.query(User).get(current_user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.has_role('field_officer'):
            raise HTTPException(status_code=403, detail="Officer access required")

        return fn(*args, current_user_id=current_user_id, db=db, **kwargs)
    return wrapper


def commissioner_required(fn):
    @wraps(fn)
    def wrapper(*args, current_user_id: int = None, db=None, **kwargs):
        user = db.query(User).get(current_user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.has_role('commissioner'):
            raise HTTPException(status_code=403, detail="Commissioner access required")

        return fn(*args, current_user_id=current_user_id, db=db, **kwargs)
    return wrapper
