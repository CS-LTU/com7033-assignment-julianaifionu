import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.auth.auth import (
    authenticate_user,
    get_user_by_id,
)
from models.users.user_model import update_user_activation
from utils.services_logging import log_action
from utils.validations import (
    validate_login_form,
    validate_activation_passwords,
)
from models.auth.activation import (
    get_valid_activation_user,
    mark_token_used,
)
from models.clinicians.clinician_model import (
    get_user_clinician_id,
    is_clinician_archived,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET"])
def login_get():
    if session.get("user_id"):
        return redirect(url_for("clinician.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def login_post():
    if session.get("user_id"):
        return redirect(url_for("index"))

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
            return redirect(url_for("auth.activate_get"))
        
        clinician = get_user_clinician_id(user["id"])
        
        # Ensure clinician is not archived
        if clinician and is_clinician_archived(clinician):
            raise ValueError("This account is inactive. Contact admin.")

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
        return redirect(url_for("index"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("auth.login_get"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login_get"))


@auth_bp.route("/activate/<token>", methods=["GET"])
def activate_account_get(token):
    user_id = get_valid_activation_user(token)

    if not user_id:
        return render_template("clinicians/activation_invalid.html")

    return render_template("clinicians/activate.html", token=token)


@auth_bp.route("/activate/<token>", methods=["POST"])
def activate_account_post(token):
    user_id = get_valid_activation_user(token)

    if not user_id:
        flash("Invalid or expired activation link.", "danger")
        return redirect(url_for("auth.login_get"))

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
        return redirect(url_for("auth.login_get"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("auth.activate_account_get", token=token))

    except (Exception, sqlite3.Error):
        flash("An unexpected error occurred.", "danger")
        return redirect(url_for("auth.activate_account_get", token=token))
