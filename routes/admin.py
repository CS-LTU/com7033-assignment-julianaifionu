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
from utils.time_formatter import utc_now
from models.clinicians.clinician_model import (
    create_clinician_profile,
    get_all_clinicians,
    get_clinician_by_id,
    is_clinician_archived,
    update_clinician,
    archive_clinician_service,
)

from models.users.user_model import create_user
from utils.decorators import (
    admin_required,
    login_required,
)
from models.patients.sqlite_models import (
    get_all_patients_for_clinician,
    get_all_patients,
    archive_patient_service,
)
from utils.services_logging import log_action
from utils.validations import validate_registration_form
from models.auth.activation import generate_activation_token
from utils.current_user import get_current_user
from models.admin.admin_models import (
    get_user_admin_stats,
    get_clinician_admin_stats,
    get_patient_admin_stats,
)

admin_bp = Blueprint("admin", __name__)


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
            "auth.activate_account_get", token=raw_token, _external=True
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


@admin_bp.route("/clinicians", methods=["GET"])
@login_required
@admin_required
def view_clinicians():
    clinicians = get_all_clinicians()

    return render_template(
        "admin/clinicians/lists.html",
        clinicians=clinicians,
    )


@admin_bp.route("/clinicians/<int:clinician_id>", methods=["GET"])
@login_required
@admin_required
def view_clinician(clinician_id):
    role_name = session.get("role_name")
    clinician = get_clinician_by_id(clinician_id)
    patients = get_all_patients_for_clinician(clinician_id)

    return render_template(
        "admin/clinicians/show.html",
        clinician=clinician,
        patients=patients,
        role_name=role_name,
    )


@admin_bp.route("/clinicians/<int:clinician_id>/edit", methods=["GET"])
@login_required
@admin_required
def edit_clinician_get(clinician_id):
    try:
        is_archived = is_clinician_archived(clinician_id)

        if is_archived:
            raise ValueError("Cannot edit an archived clinician.")

        clinician = get_clinician_by_id(clinician_id)
        role_name = session.get("role_name")

        return render_template(
            "admin/clinicians/edit.html",
            clinician=clinician,
            role_name=role_name,
        )

    except sqlite3.Error as e:
        flash(f"Error loading clinician data: {e}", "danger")
        return redirect(url_for("admin.view_clinician", clinician_id=clinician_id))
    except ValueError as e:
        flash(f"{e}", "danger")
        return redirect(url_for("admin.view_clinician", clinician_id=clinician_id))


@admin_bp.route("/clinicians/<int:clinician_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_clinician_post(clinician_id):
    try:
        is_achived = is_clinician_archived(clinician_id)
        if is_achived:
            raise ValueError("Cannot edit an archived clinician.")

        update_clinician(clinician_id, request.form)
        updated_at = utc_now()
        user_id = session.get("user_id")

        log_action(
            "CLINICIAN UPDATED",
            user_id,
            {
                "clinician_id": clinician_id,
                "updated_at": updated_at,
            },
        )
        flash("clinician updated successfully!", "success")
        return redirect(url_for("admin.view_clinician", clinician_id=clinician_id))
    except sqlite3.Error as e:
        flash(f"Error while updating clinician: {e}", "danger")
        return redirect(url_for("admin.edit_clinician_get", clinician_id=clinician_id))
    except Exception as e:
        flash(f"Unknown error occurred!: {e}", "danger")
        return redirect(url_for("admin.edit_clinician_get", clinician_id=clinician_id))


@admin_bp.route("/clinicians/<int:clinician_id>/archive", methods=["POST"])
@login_required
@admin_required
def archive_clinician(clinician_id):
    try:
        archive_clinician_service(clinician_id)
        user_id = session.get("user_id")
        log_action(
            "CLINICIAN ARCHIVED",
            user_id,
            {
                "clinician_id": clinician_id,
                "archived_at": utc_now(),
            },
        )
        flash("clinician has been archived.", "success")
        return redirect(url_for("admin.view_clinician", clinician_id=clinician_id))
    except sqlite3.Error:
        flash(f"Error archiving clinician", "danger")
        return redirect(url_for("admin.view_clinician", clinician_id=clinician_id))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("admin.view_clinician", clinician_id=clinician_id))
    except Exception:
        flash(f"Unknown error occurred!", "danger")
        return redirect(url_for("admin.view_clinician", clinician_id=clinician_id))


@admin_bp.route("/patients", methods=["GET"])
@login_required
@admin_required
def view_patients():
    patients = get_all_patients()
    return render_template(
        "admin/patients/list.html",
        patients=patients,
    )


@admin_bp.route("/patients/<int:patient_id>/archive", methods=["POST"])
@login_required
@admin_required
def admin_archive_patient(patient_id):
    try:
        archive_patient_service(patient_id)

        user_id = session.get("user_id")

        log_action(
            "PATIENT ARCHIVED",
            user_id,
            {
                "patient_id": patient_id,
                "archived_at": utc_now(),
            },
        )
        flash("Patient has been archived.", "success")
        return redirect(url_for("admin.view_patients"))
    except (sqlite3.Error, Exception):
        flash(f"An error occurred", "danger")
        return redirect(url_for("admin.view_patients"))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("admin.view_patients"))
