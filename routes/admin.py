from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    Blueprint,
)
import sqlite3
from models.clinicians.clinician_model import (
    create_clinician_profile,
    get_all_clinicians,
)
from models.users.user_model import create_user
from utils.decorators import (
    admin_required,
    login_required,
)
from models.patients.sqlite_models import get_all_patients
from utils.services_logging import log_action
from utils.validations import validate_registration_form
from models.auth.activation import generate_activation_token
from utils.current_user import get_current_user
from models.admin.admin_models import (
    get_user_admin_stats,
    get_clinician_admin_stats,
    get_patient_admin_stats,
)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@admin_required
def dashboard():
    user = get_current_user()

    clinician_stats = get_clinician_admin_stats()
    patient_stats = get_patient_admin_stats()
    user_stats = get_user_admin_stats()
    clinicians = get_all_clinicians()
    patients = get_all_patients()

    return render_template(
        "admin/dashboard.html",
        user=user,
        clinician_stats=clinician_stats,
        patient_stats=patient_stats,
        user_stats=user_stats,
        clinicians=clinicians,
        patients=patients,
    )


@admin_bp.route("/clinicians/create", methods=["GET"])
@admin_required
def create_clinician_get():
    return render_template("admin/clinicians/create.html")


@admin_bp.route("/clinicians/create", methods=["POST"])
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

        return redirect(
            url_for("admin.activation_link", activation_link=activation_link)
        )

    except sqlite3.Error as e:
        flash(f"Database error occurred. {e}", "danger")
        return redirect(url_for("admin.create_clinician_get"))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("admin.create_clinician_get"))


@admin_bp.route("/clinicians/activation-link", methods=["GET"])
def activation_link():
    activation_link = request.args.get("activation_link")

    return render_template(
        "admin/clinicians/activation_link.html", activation_link=activation_link
    )
