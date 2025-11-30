from functools import wraps
from flask import session, redirect, url_for, flash
from models.patients.sqlite_models import get_patient_by_id
from models.clinicians.clinician_model import get_clinician_user_id


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


def clinician_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        role_name = session.get("role_name")

        if role_name != "clinician":
            flash("Clinician access required.", "danger")
            return redirect(url_for("dashboard"))

        return f(*args, **kwargs)

    return wrapper


def patient_clinician_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")
        role_name = session.get("role_name")

        if not user_id:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))

        patient_id = kwargs.get("patient_id")
        if patient_id is None:
            flash("Invalid patient selected.", "danger")
            return redirect(url_for("dashboard"))

        patient = get_patient_by_id(patient_id)
        if not patient:
            flash("Patient not found.", "danger")
            return redirect(url_for("dashboard"))

        patient_owner_clinician_id = patient["clinician_id"]

        owner_row = get_clinician_user_id(patient_owner_clinician_id)
        if not owner_row:
            flash("Clinician information missing.", "danger")
            return redirect(url_for("dashboard"))

        clinician_user_id = owner_row["user_id"]
        
        if role_name == "clinician" and user_id == clinician_user_id:
            return f(*args, **kwargs)

        if role_name == "admin":
            return f(*args, **kwargs)

        flash("You do not have permission to access this patient record.", "danger")
        return redirect(url_for("dashboard"))

    return wrapper
