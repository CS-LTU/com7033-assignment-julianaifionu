import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.time_formatter import utc_now
from models.clinicians.clinician_model import (
    get_user_clinician_id,
    get_clinician_dashboard_stats,
)
from utils.decorators import (
    login_required,
    clinician_required,
    patient_clinician_or_admin_required,
    patient_clinician_only,
)
from models.patients.sqlite_models import (
    get_all_patients_for_clinician,
    update_patient,
    create_patient,
    get_patient_by_id,
    archive_patient_service,
    is_patient_archived,
)
from utils.services_logging import log_action
from models.patients.mongo_models import (
    insert_lifestyle,
    insert_medical_history,
    get_lifestyle,
    get_medical_history,
    update_lifestyle,
    update_medical_history,
)

clinician_bp = Blueprint("clinician", __name__)


@clinician_bp.route("/dashboard", methods=["GET"])
@login_required
@clinician_required
def dashboard():
    user_id = session.get("user_id")
    clinician_id = get_user_clinician_id(user_id)
    clinician_stats = get_clinician_dashboard_stats(clinician_id)

    patients = get_all_patients_for_clinician(clinician_id)
    return render_template(
        "clinicians/dashboard.html",
        patients=patients,
        clinician_stats=clinician_stats,
    )


@clinician_bp.route("/patients/new", methods=["GET"])
@login_required
@clinician_required
def create_patient_get():
    return render_template("clinicians/patients/create.html")


@clinician_bp.route("/patients/new", methods=["POST"])
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
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("clinician.create_patient_get"))

    except sqlite3.Error as e:
        flash(f"Error creating patient: {e}", "danger")
        return redirect(url_for("clinician.create_patient_get"))
    except Exception as e:
        flash(f"Unknown error occurred!: {e}", "danger")
        return redirect(url_for("clinician.create_patient_get"))


@clinician_bp.route("/patients/<int:patient_id>/edit", methods=["GET"])
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
            "clinicians/patients/edit.html",
            patient=patient,
            lifestyle=lifestyle,
            medical=medical,
            role=role,
        )

    except sqlite3.Error as e:
        flash(f"Error loading patient data: {e}", "danger")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
    except ValueError as e:
        flash(f"{e}", "danger")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))


@clinician_bp.route("/patients/<int:patient_id>/edit", methods=["POST"])
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
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))

    except sqlite3.Error as e:
        flash(f"Error while updating patient: {e}", "danger")
        return redirect(url_for("clinician.edit_patient_get", patient_id=patient_id))
    except Exception as e:
        flash(f"Unknown error occurred!: {e}", "danger")
        return redirect(url_for("clinician.edit_patient_get", patient_id=patient_id))


@clinician_bp.route("/patients/<int:patient_id>", methods=["GET"])
@login_required
@patient_clinician_or_admin_required
def view_patient(patient_id):
    patient = get_patient_by_id(patient_id)
    lifestyle = get_lifestyle(patient_id)
    medical = get_medical_history(patient_id)

    role_name = session.get("role_name")

    return render_template(
        "clinicians/patients/show.html",
        patient=patient,
        lifestyle=lifestyle,
        medical=medical,
        role=role_name,
    )


@clinician_bp.route("/patients/<patient_id>/archive", methods=["POST"])
@login_required
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
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
    except sqlite3.Error:
        flash(f"Error archiving patient", "danger")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
    except Exception:
        flash(f"Unknown error occurred!", "danger")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))


@clinician_bp.route("/patients", methods=["GET"])
@login_required
@clinician_required
def view_patients():
    user_id = session.get("user_id")
    clinician_id = get_user_clinician_id(user_id)
    patients = get_all_patients_for_clinician(clinician_id)

    return render_template(
        "clinicians/patients/list.html",
        patients=patients,
    )
