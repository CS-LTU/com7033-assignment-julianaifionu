from functools import wraps
from flask import session, redirect, url_for, flash
from models.patients.mongo_models import get_patient_by_id
from utils.current_user import get_current_user


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login_get"))
        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        role_name = session.get("role_name")

        if not user_id:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login_get"))

        if role_name != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return wrapper


def clinician_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        role_name = session.get("role_name")

        if role_name != "clinician":
            flash("Clinician access required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return wrapper

def auditor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        role_name = session.get("role_name")

        if role_name != "auditor":
            flash("auditor access required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return wrapper


def archived_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()

        if not user:
            flash("Please login.", "warning")
            return redirect(url_for("auth.login_get"))

        if user["is_archived"]:
            session.clear()
            flash("Your account has been archived. Contact admin.", "danger")
            return redirect(url_for("auth.login_get"))

        return f(*args, **kwargs)

    return wrapper
