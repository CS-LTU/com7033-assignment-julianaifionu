import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.time_formatter import utc_now
from utils.decorators import login_required, clinician_required, archived_check
from models.auth.auth import get_user_by_id
from utils.services_logging import log_action
from models.patients.mongo_models import (
    create_patient,
    get_patient_clinician_stats,
    get_all_patients,
    get_first_10_patients,
    delete_patient,
    update_patient,
    get_patient_by_id,
)

clinician_bp = Blueprint("clinician", __name__)


@clinician_bp.route("/dashboard", methods=["GET"])
@archived_check
@login_required
@clinician_required
def dashboard():
    clinician_stats = get_patient_clinician_stats()
    patients = get_first_10_patients()

    return render_template(
        "clinicians/dashboard.html",
        patients=patients,
        clinician_stats=clinician_stats,
    )


@clinician_bp.route("/patients/new", methods=["GET"])
@archived_check
@login_required
@clinician_required
def create_patient_get():
    return render_template("clinicians/patients/create.html")


@clinician_bp.route("/patients/new", methods=["POST"])
@archived_check
@login_required
@clinician_required
def create_patient_post():
    try:
        user_id = session.get("user_id")
        # Create patient in MongoDB
        patient_id = create_patient(user_id, request.form)
        log_action(
            "NEW PATIENT CREATED",
            {
                "patient_id": patient_id,
                "action_by": user_id,
                "action_at": utc_now(),
            },
        )

        flash("Patient created successfully!", "success")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("clinician.create_patient_get"))
    except (sqlite3.Error, Exception) as e:
        flash(f"Unknown error occurred! {e}", "danger")
        return redirect(url_for("clinician.create_patient_get"))


@clinician_bp.route("/patients/<string:patient_id>/edit", methods=["GET"])
@archived_check
@login_required
@clinician_required
def edit_patient_get(patient_id):
    try:
        patient = get_patient_by_id(patient_id)
        role = session.get("role_name")

        if not patient:
            raise ValueError("Cannot find patient.")

        return render_template(
            "clinicians/patients/edit.html",
            patient=patient,
            role=role,
        )
    except (sqlite3.Error, Exception):
        flash(f"Unknown error occurred!", "danger")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
    except ValueError as e:
        flash(f"{e}", "danger")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))


@clinician_bp.route("/patients/<string:patient_id>/edit", methods=["POST"])
@archived_check
@login_required
@clinician_required
def edit_patient_post(patient_id):
    try:
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise ValueError("Cannot find patient.")

        user_id = session.get("user_id")
        update_patient(patient_id, request.form, user_id)

        log_action(
            "PATIENT UPDATED",
            {
                "patient_id": patient_id,
                "action_by": user_id,
                "action_at": utc_now(),
            },
        )

        flash("Patient updated successfully!", "success")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
    except (sqlite3.Error, Exception) as e:
        flash(f"Unknown error occurred!: {e}", "danger")
        return redirect(url_for("clinician.edit_patient_get", patient_id=patient_id))


@clinician_bp.route("/patients/<string:patient_id>", methods=["GET"])
@archived_check
@login_required
@clinician_required
def view_patient(patient_id):
    patient = get_patient_by_id(patient_id)
    user = get_user_by_id(patient.get("created_by"))
    patient_creator = user["full_name"] if user else "Unknown"

    role_name = session.get("role_name")

    return render_template(
        "clinicians/patients/show.html",
        patient_creator=patient_creator,
        patient=patient,
        role=role_name,
    )


@clinician_bp.route("/patients", methods=["GET"])
@archived_check
@login_required
@clinician_required
def view_patients():
    patients = get_all_patients()
    return render_template(
        "clinicians/patients/list.html",
        patients=patients,
    )


@clinician_bp.route("/patients/<string:patient_id>/delete", methods=["POST"])
@archived_check
@login_required
@clinician_required
def delete_patient_post(patient_id):
    try:
        user_id = session.get("user_id")
        delete_patient(patient_id)

        log_action(
            "PATIENT DELETED",
            {
                "patient_id": patient_id,
                "action_by": user_id,
                "action_at": utc_now(),
            },
        )
        flash("Patient deleted successfully.", "success")
        return redirect(url_for("clinician.view_patients", patient_id=patient_id))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
    except (Exception, sqlite3.Error):
        flash(f"Unknown error occurred!", "danger")
        return redirect(url_for("clinician.view_patient", patient_id=patient_id))
