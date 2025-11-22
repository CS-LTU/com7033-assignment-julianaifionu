from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user_role = session.get("user_role")

        if not user_id:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))

        if user_role and user_role != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("home"))

        return f(*args, **kwargs)

    return wrapper
