from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("login_get"))
        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        role_name = session.get("role_name")

        if not user_id:
            flash("Please log in first.", "warning")
            return redirect(url_for("login_get"))

        if role_name != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard"))

        return f(*args, **kwargs)

    return wrapper