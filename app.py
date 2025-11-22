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


# Route for the home page
@app.route("/")
@login_required
def home():
    user_id = session.get("user_id")
    user = get_user_by_id(user_id)

    if not user:
        return redirect(url_for("login"))

    return render_template("home.html", user=user, patients=PATIENTS)


# Route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    user_id = session.get("user_id")

    if user_id:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        try:
            # ----- value checks -----
            if not (email and password):
                raise ValueError("Please enter both email and password.")

            # ----- Authenticate user -----
            user = authenticate_user(email, password)
            if not user:
                raise ValueError("Invalid email or password")

            # if the user hasn't activated their account yet
            if not user["is_active"]:
                session["pending_activation_id"] = user["id"]
                flash("Please activate your account before continuing.", "info")
                return redirect(url_for("activate"))

            # Normal login flow
            # set secure session cookies
            session["user_id"] = user["id"]
            session["user_role"] = user["role"]

            flash(f"✅ Logged in successfully!", "success")
            return redirect(url_for("home"))

        except ValueError as e:
            flash(f"⚠ Validation error: {e}", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


# Route for logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


# Route for invite / register user
@app.route("/register", methods=["GET", "POST"])
@admin_required
def register():
    try:
        temp_password = str(secrets.token_hex(4))

        if request.method == "POST":
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            role = request.form.get("role", "").strip().lower()

            # Validate required fields
            if not (first_name and last_name and email and role):
                raise ValueError("All fields are required.")

            if not Config.EMAIL_PATTERN.fullmatch(email):
                raise ValueError("Email format is invalid.")

            # Check for existing user
            user = get_user_by_email(email)
            if user:
                raise ValueError("A user with this email already exists.")

            conn = get_db()
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO users (first_name, last_name, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                (first_name, last_name, email, hash_password(temp_password), role),
            )
            conn.commit()
            conn.close()

            flash(
                f"Registered successfully! Temp password: {temp_password}",
                "success",
            )
            return redirect(url_for("home"))

    except sqlite3.IntegrityError:
        flash(
            "User already exists.",
            "danger",
        )
        return redirect(url_for("register"))

    except ValueError as e:
        flash(str(e), "danger")

    return render_template("register.html", temp_password=temp_password)


# Route for account activation
@app.route("/activate", methods=["GET", "POST"])
def activate():
    user_id = session.get("pending_activation_id")
    if not user_id:
        flash("No account pending activation.", "warning")
        return redirect(url_for("login"))

    # Find the user
    user = get_user_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not (new_password and confirm_password):
            flash("Please fill in both password fields.", "warning")
            return render_template("activate.html", email=user["email"])

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("activate.html", email=user["email"])

        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("activate.html", email=user["email"])

        # Update password and mark account as activated
        password_hash = hash_password(new_password)
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
						UPDATE users
						SET password_hash = ?, is_active = ?
						WHERE id = ?
    				""",
            (password_hash, True, user["id"]),
        )
        conn.commit()
        conn.close()

        session.pop("pending_activation_id", None)

        flash("Account activated! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("activate.html", email=user["email"])


if __name__ == "__main__":
    app.run(debug=True, port=3000)
