import sqlite3
import secrets

from flask import Flask, render_template, request, redirect, url_for, flash, session
from utils.auth import (
    authenticate_user,
    get_user_by_id,
)
from utils.config import Config
from utils.initialize import initialize
from utils.decorators import admin_required, login_required
from utils.services_logging import log_action
from utils.queries import create_user, update_user_activation
from utils.validations import (
    validate_registration_form,
    validate_login_form,
    validate_activation_passwords,
)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

initialize()

PATIENTS = [
    {
        "patient_id": 1,
        "username": "mary",
        "gender": "female",
        "age": 34,
        "ever_married": True,
        "work_type": "private",
        "residence_type": "Urban",
    },
    {
        "patient_id": 2,
        "username": "John",
        "gender": "male",
        "age": 52,
        "ever_married": True,
        "work_type": "govt_job",
        "residence_type": "Rural",
    },
    {
        "patient_id": 3,
        "username": "Jane",
        "gender": "female",
        "age": 12,
        "ever_married": False,
        "work_type": "children",
        "residence_type": "Urban",
    },
]


# --------------------------------------
# Context processor to inject user info into templates
# --------------------------------------
@app.context_processor
def inject_user():
    """
    Make the logged-in user's first name and role globally available
    to all templates.
    """

    user_id = session.get("user_id")
    if not user_id:
        return dict(fist_name=None, role=None)

    user = get_user_by_id(user_id)

    if not user:
        return dict(first_name=None, role=None)

    return dict(first_name=user["first_name"], role=user["role"])


# --------------------------------------
# GET: Show home page
# --------------------------------------
@app.route("/")
@login_required
def home():
    user_id = session.get("user_id")
    user = get_user_by_id(user_id)

    if not user:
        return redirect(url_for("login_get"))

    return render_template("home.html", user=user, patients=PATIENTS)


# --------------------------------------
# GET: Show login form
# --------------------------------------
@app.route("/login", methods=["GET"])
def login_get():
    if session.get("user_id"):
        return redirect(url_for("home"))

    return render_template("login.html")


# --------------------------------------
# POST: Handle user login logic
# --------------------------------------
@app.route("/login", methods=["POST"])
def login_post():
    if session.get("user_id"):
        return redirect(url_for("home"))

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    try:
        validate_login_form(email, password)

        user = authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid email or password.")

        # Require activation first
        if not user["is_active"]:
            session["pending_activation_id"] = user["id"]
            flash("Please activate your account before continuing.", "info")
            return redirect(url_for("activate_get"))

        session["user_id"] = user["id"]
        session["user_role"] = user["role"]

        log_action(
            "LOGIN",
            session.get("user_id"),
            {
                "login_user_id": user["id"],
                "login_user_email": user["email"],
                "login_user_role": user["role"],
            },
        )

        flash("Logged in successfully!", "success")
        return redirect(url_for("home"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("login_get"))


# --------------------------------------
# GET: Show registration form
# --------------------------------------
@app.route("/register", methods=["GET"])
@admin_required
def register_get():
    return render_template("register.html")


# --------------------------------------
# POST: Handle user registration logic
# --------------------------------------
@app.route("/register", methods=["POST"])
@admin_required
def register_post():
    temp_password = str(secrets.token_hex(4))

    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "").strip().lower()

    try:
        validate_registration_form(first_name, last_name, email, role)
        new_user_id = create_user(first_name, last_name, email, role, temp_password)

        log_action(
            "REGISTER",
            session.get("user_id"),
            {
                "created_user_id": new_user_id,
                "created_user_email": email,
                "created_user_role": role,
            },
        )

        flash(f"Registered successfully! Temp password: {temp_password}", "success")
        return redirect(url_for("home"))

    except sqlite3.Error:
        flash("Database error occurred.", "danger")
        return redirect(url_for("register_get"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("register_get"))


# -----------------------------
# GET: Show activation form
# -----------------------------
@app.route("/activate", methods=["GET"])
def activate_get():
    user_id = session.get("pending_activation_id")

    if not user_id:
        flash("No pending activation found. Please log in.", "danger")
        return redirect(url_for("login_get"))

    user = get_user_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login_get"))

    return render_template("activate.html")


# -----------------------------
# POST: Handle user activation logic
# -----------------------------
@app.route("/activate", methods=["POST"])
def activate_post():
    try:
        user_id = session.get("pending_activation_id")
        if not user_id:
            raise ValueError("No pending activation found. Please log in.")

        user = get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found.")

        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        validate_activation_passwords(new_password, confirm_password)

        update_user_activation(user_id, new_password)

        log_action(
            "ACTIVATE",
            user_id,
            {
                "user_email": user["email"],
                "user_role": user["role"],
            },
        )

        # Clean up activation session
        session.pop("pending_activation_id", None)

        flash("Account activated! You can now log in.", "success")
        return redirect(url_for("login_get"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("activate_get"))

    except sqlite3.Error:
        flash("Database error occurred during activation.", "danger")
        return redirect(url_for("activate_get"))

    except Exception:
        flash("An unexpected error occurred.", "danger")
        return redirect(url_for("activate_get"))


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
