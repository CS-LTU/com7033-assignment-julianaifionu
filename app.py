import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.auth.auth import (
    authenticate_user,
    get_user_by_id,
)
from utils.time_formatter import utc_now
from models.clinicians.clinician_model import (
    create_clinician_profile,
    get_all_clinicians,
    get_user_clinician_id,
    archived_patients_clinician_count,
    active_patients_clinician_count,
    new_patients_clinician_today_count,
)

from models.users.user_model import create_user, update_user_activation
from utils.config import Config
from models.initialize import initialize
from utils.decorators import (
    admin_required,
    login_required,
    clinician_required,
    patient_clinician_or_admin_required,
    patient_clinician_only,
)
from models.patients.sqlite_models import (
    get_all_patients,
    get_all_patients_for_clinician,
    update_patient,
    create_patient,
    get_patient_by_id,
    archive_patient_service,
    is_patient_archived,
    total_archived_patients_count,
    total_active_patients_count,
    new_patients_today_count,
)
from utils.services_logging import log_action
from utils.validations import (
    validate_registration_form,
    validate_login_form,
    validate_activation_passwords,
)
from models.auth.activation import (
    generate_activation_token,
    get_valid_activation_user,
    mark_token_used,
)
from utils.current_user import get_current_user
from models.patients.mongo_models import (
    insert_lifestyle,
    insert_medical_history,
    get_lifestyle,
    get_medical_history,
    update_lifestyle,
    update_medical_history,
)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

initialize()


# --------------------------------------
# Custom filter to format ISO UTC strings nicely
# --------------------------------------
@app.template_filter("humanize_date")
def humanize_date(iso_string: str) -> str:
    """
    Converts ISO 8601 string to '30 Nov 2025, 10:31 PM' format.
    """
    dt = datetime.fromisoformat(iso_string)
    return dt.strftime("%d %b %Y, %I:%M %p")


# --------------------------------------
# Context processor to inject user info into templates
# --------------------------------------
@app.context_processor
def inject_user():
    """
    Make logged-in user's username and role name globally available
    to all templates.
    """
    current_user = get_current_user()

    if not current_user:
        return dict(username=None, role_name=None)

    return dict(username=current_user["username"], role_name=current_user["role_name"])


# --------------------------------------
# GET: Handle the index page
# --------------------------------------
@app.route("/", methods=["GET"])
@login_required
def index():
    current_user = get_current_user()

    if current_user and current_user["role_name"] == "admin":
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("dashboard"))


# --------------------------------------
# GET: Show admin dashboard page
# --------------------------------------
@app.route("/admin/dashboard", methods=["GET"])
@login_required
@admin_required
def admin_dashboard():
    user = get_current_user()
    clinicians = get_all_clinicians()
    patients = get_all_patients()
    archived_patients = total_archived_patients_count()
    active_patients = total_active_patients_count()
    new_patients_today = new_patients_today_count()

    return render_template(
        "admin/dashboard.html",
        user=user,
        clinicians=clinicians,
        patients=patients,
        archived_patients=archived_patients,
        active_patients=active_patients,
        new_patients_today=new_patients_today,
    )


# --------------------------------------
# GET: Show clinician dashboard page
# --------------------------------------
@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    user_id = session.get("user_id")
    role_name = session.get("role_name")

    if role_name == "admin":
        return redirect(url_for("admin_dashboard"))

    clinician_id = get_user_clinician_id(user_id)
    patients = get_all_patients_for_clinician(clinician_id)
    archived_patients = archived_patients_clinician_count(clinician_id)
    active_patients = active_patients_clinician_count(clinician_id)
    new_patients_today = new_patients_clinician_today_count(clinician_id)

    return render_template(
        "clinicians/dashboard.html",
        patients=patients,
        archived_patients=archived_patients,
        active_patients=active_patients,
        new_patients_today=new_patients_today,
    )


# --------------------------------------
# GET: Show login form
# --------------------------------------
@app.route("/login", methods=["GET"])
def login_get():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# --------------------------------------
# POST: Handle user login logic
# --------------------------------------
@app.route("/login", methods=["POST"])
def login_post():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    try:
        validate_login_form(username, password)

        user = authenticate_user(username, password)
        if not user:
            raise ValueError("Invalid username or password.")

        # Ensure account is activated
        if not user["is_active"]:
            flash("Please activate your account before continuing.", "info")
            return redirect(url_for("activate_get"))

        full_user = get_user_by_id(user["id"])
        session["user_id"] = full_user["id"]
        session["role_name"] = full_user["role_name"]
        session["role_id"] = full_user["role_id"]

        # Log the login action
        log_action(
            "LOGIN",
            session.get("user_id"),
            {
                "username": full_user["username"],
                "role": full_user["role_name"],
            },
        )

        flash("Logged in successfully!", "success")
        return redirect(url_for("dashboard"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("login_get"))


# --------------------------------------
# GET: Show registration form
# --------------------------------------
@app.route("/clinicians/create", methods=["GET"])
@admin_required
def create_clinician_get():
    return render_template("admin/create_clinician.html")


# --------------------------------------
# POST: Handle user registration logic
# --------------------------------------
@app.route("/clinicians/create", methods=["POST"])
@admin_required
def create_clinician_post():
    username = (request.form.get("username") or "").strip()
    full_name = (request.form.get("full_name") or "").strip()
    specialization = (request.form.get("specialization") or "").strip()
    license_number = (request.form.get("license_number") or "").strip()

    try:
        validate_registration_form(username, license_number, "clinician")
        user_id = create_user(username, "clinician")

        create_clinician_profile(
            user_id=user_id,
            full_name=full_name,
            specialization=specialization,
            license_number=license_number,
        )

        raw_token = generate_activation_token(user_id)
        activation_link = url_for(
            "activate_account_get", token=raw_token, _external=True
        )

        # Log event
        log_action(
            "INVITE_CLINICIAN",
            session.get("user_id"),
            {
                "invited_user_id": user_id,
                "username": username,
                "activation_link": activation_link,
            },
        )

        return redirect(url_for("user_created", activation_link=activation_link))

    except sqlite3.Error:
        flash("Database error occurred.", "danger")
        return redirect(url_for("create_clinician_get"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("create_clinician_get"))


# --------------------------------------
# GET: Show success user creation page
# --------------------------------------
@app.route("/admin/user_created", methods=["GET"])
def user_created():
    activation_link = request.args.get("activation_link")

    return render_template("admin/user_created.html", activation_link=activation_link)


# -----------------------------
# GET: Show activation form
# -----------------------------
@app.route("/activate/<token>", methods=["GET"])
def activate_account_get(token):
    user_id = get_valid_activation_user(token)

    if not user_id:
        return render_template("clinicians/activation_invalid.html")

    return render_template("clinicians/activate.html", token=token)


# -----------------------------
# POST: Handle user activation logic
# -----------------------------
@app.route("/activate/<token>", methods=["POST"])
def activate_account_post(token):
    user_id = get_valid_activation_user(token)

    if not user_id:
        flash("Invalid or expired activation link.", "danger")
        return redirect(url_for("login_get"))

    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    try:
        validate_activation_passwords(new_password, confirm_password)
        update_user_activation(user_id, new_password)

        # Mark token as used
        used_at_time = mark_token_used(token)

        # Log action
        log_action("ACCOUNT_ACTIVATED", user_id, {"used_at": used_at_time})

        flash("Your account has been activated. You can now log in.", "success")
        return redirect(url_for("login_get"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("activate_account_get", token=token))

    except (Exception, sqlite3.Error):
        flash("An unexpected error occurred.", "danger")
        return redirect(url_for("activate_account_get", token=token))


# --------------------------------------
# GET: Show create patient page
# --------------------------------------
@app.route("/patients/new", methods=["GET"])
@login_required
@clinician_required
def create_patient_get():
    return render_template("patients/new_patient.html")


# --------------------------------------
# POST: Handle create patient logic
# --------------------------------------
@app.route("/patients/new", methods=["POST"])
@login_required
@clinician_required
def create_patient_post():
    try:
        user_id = session.get("user_id")
        clinician_id = get_user_clinician_id(user_id)

        # Create patient in SQLite
        patient_id = create_patient(clinician_id, request.form)

        # Insert medical history into MongoDB
        insert_medical_history(patient_id, request.form)

        # Insert lifestyle info into MongoDB
        insert_lifestyle(patient_id, request.form)

        patient = get_patient_by_id(patient_id)

        log_action(
            "NEW PATIENT CREATED",
            user_id,
            {
                "patient_id": patient_id,
                "clinician_id": clinician_id,
                "created_at": patient["created_at"],
            },
        )

        flash("Patient created successfully!", "success")
        return redirect(url_for("view_patient", patient_id=patient_id))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("create_patient_get"))

    except sqlite3.Error as e:
        flash(f"Error creating patient: {e}", "danger")
        return redirect(url_for("create_patient_get"))
    except Exception as e:
        flash(f"Unknown error occurred!: {e}", "danger")
        return redirect(url_for("create_patient_get"))


# --------------------------------------
# GET: Show update patient page
# --------------------------------------
@app.route("/patients/<int:patient_id>/edit", methods=["GET"])
@login_required
@patient_clinician_only
def edit_patient_get(patient_id):
    try:
        is_achived = is_patient_archived(patient_id)

        if is_achived:
            raise ValueError("Cannot edit an archived patient.")

        patient = get_patient_by_id(patient_id)
        lifestyle = get_lifestyle(patient_id)
        medical = get_medical_history(patient_id)

        role = session.get("role_name")

        return render_template(
            "patients/edit_patient.html",
            patient=patient,
            lifestyle=lifestyle,
            medical=medical,
            role=role,
        )

    except sqlite3.Error as e:
        flash(f"Error loading patient data: {e}", "danger")
        return redirect(url_for("view_patient", patient_id=patient_id))
    except ValueError as e:
        flash(f"{e}", "danger")
        return redirect(url_for("view_patient", patient_id=patient_id))


# --------------------------------------
# POST: Handle update patient logic
# --------------------------------------
@app.route("/patients/<int:patient_id>/edit", methods=["POST"])
@login_required
@patient_clinician_only
def edit_patient_post(patient_id):
    try:
        is_achived = is_patient_archived(patient_id)
        if is_achived:
            raise ValueError("Cannot edit an archived patient.")

        update_patient(patient_id, request.form)
        update_lifestyle(patient_id, request.form)
        update_medical_history(patient_id, request.form)
        updated_at = utc_now()

        user_id = session.get("user_id")
        clinician_id = get_user_clinician_id(user_id)

        log_action(
            "PATIENT UPDATED",
            user_id,
            {
                "patient_id": patient_id,
                "clinician_id": clinician_id,
                "updated_at": updated_at,
            },
        )

        flash("Patient updated successfully!", "success")
        return redirect(url_for("view_patient", patient_id=patient_id))

    except sqlite3.Error as e:
        flash(f"Error while updating patient: {e}", "danger")
        return redirect(url_for("edit_patient_get", patient_id=patient_id))
    except Exception as e:
        flash(f"Unknown error occurred!: {e}", "danger")
        return redirect(url_for("edit_patient_get", patient_id=patient_id))


# --------------------------------------
# GET: View single patient detail page
# --------------------------------------
@app.route("/patients/<int:patient_id>", methods=["GET"])
@login_required
@patient_clinician_or_admin_required
def view_patient(patient_id):
    patient = get_patient_by_id(patient_id)
    lifestyle = get_lifestyle(patient_id)
    medical = get_medical_history(patient_id)

    role_name = session.get("role_name")

    return render_template(
        "patients/view_patient.html",
        patient=patient,
        lifestyle=lifestyle,
        medical=medical,
        role=role_name,
    )


# --------------------------------------
# POST: Handle archive patient logic
# --------------------------------------
@app.route("/patients/<patient_id>/archive", methods=["POST"])
@patient_clinician_only
def archive_patient(patient_id):
    try:
        archive_patient_service(patient_id)

        user_id = session.get("user_id")
        clinician_id = get_user_clinician_id(user_id)

        log_action(
            "PATIENT ARCHIVED",
            user_id,
            {
                "patient_id": patient_id,
                "clinician_id": clinician_id,
                "archived_at": utc_now(),
            },
        )
        flash("Patient has been archived.", "success")
        return redirect(url_for("view_patient", patient_id=patient_id))
    except sqlite3.Error:
        flash(f"Error archiving patient", "danger")
        return redirect(url_for("view_patient", patient_id=patient_id))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("view_patient", patient_id=patient_id))
    except Exception:
        flash(f"Unknown error occurred!", "danger")
        return redirect(url_for("view_patient", patient_id=patient_id))


# --------------------------------------
# POST: Handle logout
# --------------------------------------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login_get"))


if __name__ == "__main__":
    app.run(debug=True, port=3000)
