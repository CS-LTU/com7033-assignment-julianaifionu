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
    update_user,
    delete_user_service,
)
from utils.decorators import admin_required, login_required
from utils.services_logging import log_action
from models.auth.validations import validate_registration_form
from models.auth.activation import generate_activation_token
from models.admin.admin_models import get_user_admin_stats, get_all_users, search_user
from models.patients.mongo_models import get_patient_admin_stats
from models.auth.auth import get_user_by_id

admin_bp = Blueprint("admin", __name__)


# Admin routes
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
    return render_template("admin/users/create.html", form_data={})


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
            session.get("user_id"),
            {
                "action_on": new_user_id,
                "action_at": utc_now(),
            },
        )
        flash("User created successfully!", "success")
        return redirect(
            url_for("admin.activation_link", activation_link=activation_link)
        )
    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/users/create.html",
            form_data={
                "username": username,
                "full_name": full_name,
                "role_name": role_name,
            },
        )
    except sqlite3.Error as e:
        flash(f"An error occurred", "danger")
        return render_template(
            "admin/users/create.html",
            form_data={
                "username": username,
                "full_name": full_name,
                "role_name": role_name,
            },
        )


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
    return render_template(
        "admin/users/show.html",
        user=user,
        role_name=role_name,
    )


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET"])
@login_required
@admin_required
def edit_user_get(user_id):
    try:
        user = get_user_by_id(user_id)

        if user is None:
            raise ValueError("User does not exist.")

        if user["role_name"].lower() == "admin":
            raise ValueError("Cannot edit admin account.")

        return render_template(
            "admin/users/edit.html",
            user=user,
        )
    except ValueError as e:
        flash(f"{e}", "danger")
        return render_template("admin/users/edit.html", user=user)
    except sqlite3.Error as e:
        flash(f"An error occurred", "danger")
        return render_template("admin/users/edit.html", user=user)


@admin_bp.route("/users/<int:user_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_user_post(user_id):
    try:
        user = get_user_by_id(user_id)
        if user is None:
            raise ValueError("User does not exist.")

        if user["role_name"].lower() == "admin":
            raise ValueError("Cannot edit admin account.")

        update_user(user_id, request.form)
        log_action(
            "USER UPDATED",
            session.get("user_id"),
            {
                "action_on": user_id,
                "action_at": utc_now(),
            },
        )
        flash("User updated successfully!", "success")
        return redirect(url_for("admin.view_user", user_id=user_id))
    except ValueError as e:
        flash(str(e), "warning")
        return render_template(
            "admin/users/edit.html",
            user=user,
        )
    except (sqlite3.Error, Exception):
        flash(f"An error occured", "danger")
        return render_template("admin/users/edit.html", user=user)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    try:
        delete_user_service(user_id)
        log_action(
            "USER DELETED",
            session.get("user_id"),
            {
                "action_on": user_id,
                "action_at": utc_now(),
            },
        )
        flash("User has been deleted successfully.", "success")
        return redirect(url_for("admin.view_users"))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("admin.view_user", user_id=user_id))
    except (sqlite3.Error, Exception):
        flash(f"An error occurred!", "danger")
        return redirect(url_for("admin.view_user", user_id=user_id))
