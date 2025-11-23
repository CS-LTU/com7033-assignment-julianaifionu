import sqlite3
import secrets

from flask import Flask, render_template, request, redirect, url_for, flash, session
from utils.auth import (
    authenticate_user,
    get_user_by_email,
    hash_password,
    get_user_by_id,
)
from utils.config import Config
from utils.db_sqlite import get_db
from utils.initialize import initialize
from utils.decorators import admin_required, login_required
from utils.services_logging import log_action

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
        if not (email and password):
            raise ValueError("Please enter both email and password.")

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

        flash("Logged in successfully!", "success")
        log_action(
            "LOGIN",
            session.get("user_id"),
            {"first_name": user["first_name"]},
        )
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
    try:
        temp_password = str(secrets.token_hex(4))

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "").strip().lower()

        if not (first_name and last_name and email and role):
            raise ValueError("All fields are required.")

        if not Config.EMAIL_PATTERN.fullmatch(email):
            raise ValueError("Email format is invalid.")

        # Check existing user
        user = get_user_by_email(email)
        if user:
            raise ValueError("A user with this email already exists.")

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO users 
            (first_name, last_name, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (first_name, last_name, email, hash_password(temp_password), role),
        )

        action_performer = get_user_by_id(session.get("user_id"))
        if action_performer:
            log_action(
                "REGISTER",
                action_performer["id"],
                {"first_name": action_performer["first_name"]},
            )
            conn.commit()
            conn.close()

            flash(
                f"Registered successfully! Temp password: {temp_password}",
                "success",
            )
            return redirect(url_for("home"))
        else:
            conn.rollback()
            raise ValueError("The action performaer could not be identified.")

    except sqlite3.IntegrityError:
        flash("User already exists.", "danger")
        conn.rollback()
        return redirect(url_for("register_get"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("register_get"))

    finally:
        conn.close()


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

        if not (new_password and confirm_password):
            raise ValueError("Please fill in all password fields.")

        if new_password != confirm_password:
            raise ValueError("Passwords do not match.")

        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        # Hash new password
        password_hash = hash_password(new_password)

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE users
            SET password_hash = ?, is_active = ?
            WHERE id = ?
            """,
            (password_hash, True, user_id),
        )
        conn.commit()
        log_action(
            "ACTIVATE",
            user_id,
            {"first_name": user["first_name"]},
        )

        # Clean up activation session
        session.clear()

        flash("Account activated! You can now log in.", "success")
        return redirect(url_for("login_get"))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("activate_get"))

    except sqlite3.IntegrityError:
        flash("An unexpected database error occurred.", "danger")
        conn.rollback()
        return redirect(url_for("activate_get"))

    finally:
        conn.close()


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
