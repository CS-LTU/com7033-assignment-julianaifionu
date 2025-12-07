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
from models.users.user_model import (
    create_user,
    is_user_archived,
    update_user,
    archive_user_service,
)
from utils.decorators import admin_required, login_required
from utils.services_logging import log_action
from utils.validations import validate_registration_form
from models.auth.activation import generate_activation_token
from models.admin.admin_models import get_user_admin_stats, get_all_users, search_user
from models.patients.mongo_models import get_all_patients, get_patient_admin_stats
from models.auth.auth import get_user_by_id

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@admin_required
def dashboard():
    patient_stats = get_patient_admin_stats()
    user_stats = get_user_admin_stats()
    users = get_all_users()

    return render_template(
        "admin/dashboard.html",
        patient_stats=patient_stats,
        user_stats=user_stats,
        users=users,
    )


@admin_bp.route("/users/create", methods=["GET"])
@admin_required
def create_user_get():
    return render_template("admin/users/create.html")


@admin_bp.route("/users/create", methods=["POST"])
@admin_required
def create_user_post():
    username = (request.form.get("username") or "").strip()
    full_name = (request.form.get("full_name") or "").strip()
    role_name = (request.form.get("role_name") or "").strip()

    try:
        validate_registration_form(username, full_name, role_name)
        new_user_id = create_user(username, full_name, role_name)

        raw_token = generate_activation_token(new_user_id)
        activation_link = url_for(
            "auth.activate_account_get", token=raw_token, _external=True
        )

        log_action(
            "INVITE_USER",
            {
                "new_user_id": new_user_id,
                "action_by": session.get("user_id"),
                "action_at": utc_now(),
            },
        )

        return redirect(
            url_for("admin.activation_link", activation_link=activation_link)
        )

    except sqlite3.Error as e:
        flash(f"An error occurred", "danger")
        return redirect(url_for("admin.create_user_get"))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("admin.create_user_get"))


@admin_bp.route("/users/activation-link", methods=["GET"])
def activation_link():
    activation_link = request.args.get("activation_link")

    return render_template(
        "admin/users/activation_link.html", activation_link=activation_link
    )


@admin_bp.route("/users", methods=["GET"])
@login_required
@admin_required
def view_users():
    search_query = request.args.get("q", "").strip()
    users = search_user(search_query)

    return render_template(
        "admin/users/list.html", users=users, search_query=search_query
    )


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
@admin_required
def view_user(user_id):
    role_name = session.get("role_name")
    user = get_user_by_id(user_id)
    patients = get_all_patients()

    return render_template(
        "admin/users/show.html",
        user=user,
        patients=patients,
        role_name=role_name,
    )


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET"])
@login_required
@admin_required
def edit_user_get(user_id):
    try:
        is_archived = is_user_archived(user_id)
        if is_archived:
            raise ValueError("Cannot edit an archived user.")

        role_name = session.get("role_name")
        user = get_user_by_id(user_id)

        return render_template(
            "admin/users/edit.html",
            user=user,
            role_name=role_name,
        )

    except sqlite3.Error as e:
        flash(f"An error occurred", "danger")
        return redirect(url_for("admin.view_user", user_id=user_id))
    except ValueError as e:
        flash(f"{e}", "danger")
        return redirect(url_for("admin.view_user", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_user_post(user_id):
    try:
        is_archived = is_user_archived(user_id)
        if is_archived:
            raise ValueError("Cannot edit an archived user.")

        update_user(user_id, request.form)
        log_action(
            "USER UPDATED",
            {
                "action_by": session.get("user_id"),
                "action_at": utc_now(),
            },
        )
        flash("User updated successfully!", "success")
        return redirect(url_for("admin.view_user", user_id=user_id))
    except (sqlite3.Error, Exception):
        flash(f"An error occured", "danger")
        return redirect(url_for("admin.edit_user_get", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/archive", methods=["POST"])
@login_required
@admin_required
def archive_user(user_id):
    try:
        archive_user_service(user_id)
        user_session_id = session.get("user_id")
        log_action(
            "USER ARCHIVED",
            {
                "action_by": user_session_id,
                "action_at": utc_now(),
            },
        )
        flash("user has been archived.", "success")
        return redirect(url_for("admin.view_user", user_id=user_id))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("admin.view_user", user_id=user_id))
    except (sqlite3.Error, Exception):
        flash(f"An error occurred!", "danger")
        return redirect(url_for("admin.view_user", user_id=user_id))


@admin_bp.route("/patients", methods=["GET"])
@login_required
@admin_required
def view_patients():
    patients = get_all_patients()
    return render_template(
        "admin/patients/list.html",
        patients=patients,
    )
