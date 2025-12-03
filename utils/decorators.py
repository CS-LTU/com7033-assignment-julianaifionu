from functools import wraps
from flask import session, redirect, url_for, flash
from models.patients.sqlite_models import get_patient_by_id
from models.clinicians.clinician_model import get_clinician_user_id


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


def validate_patient_access(patient_id):
    """Returns (patient, clinician_user_id) or (None, None) if invalid."""
    if patient_id is None:
        return None, None

    patient = get_patient_by_id(patient_id)
    if not patient:
        return None, None

    clinician_user_id = get_clinician_user_id(patient["clinician_id"])
    if not clinician_user_id:
        return None, None

    return patient, clinician_user_id


def patient_clinician_or_admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")
        role_name = session.get("role_name")
        patient_id = kwargs.get("patient_id")
        
        patient, clinician_user_id = validate_patient_access(patient_id)

        if not patient:
            flash("Invalid patient.", "danger")
            return redirect(url_for("index"))
        
        if role_name == "admin":
            return f(*args, **kwargs)

        if role_name == "clinician" and user_id == clinician_user_id:
            return f(*args, **kwargs)


        flash("You do not have permission to access this patient record.", "danger")
        return redirect(url_for("index"))

    return wrapper


def patient_clinician_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")
        role_name = session.get("role_name")

        patient_id = kwargs.get("patient_id")
        patient, clinician_user_id = validate_patient_access(patient_id)

        if not (patient and clinician_user_id):
            return redirect(url_for("clinician.dashboard"))

        if role_name == "clinician" and user_id == clinician_user_id:
            return f(*args, **kwargs)

        flash("You do not have permission to edit this patient record.", "danger")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))

    return wrapper
