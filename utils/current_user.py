from flask import session
from models.auth.auth import get_user_by_id

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)
