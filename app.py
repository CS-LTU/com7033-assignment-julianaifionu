import os
import re
import secrets
from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from utils.auth import find_user, get_user_by_email

app = Flask(__name__)

# set STROKE_APP_SECRET_KEY via environment variable
app.secret_key = os.environ.get("STROKE_APP_SECRET_KEY", "my_dev_secret_key")

# ---------- Simple in-memory storage ----------
REGISTERED_USERS = [
    {
        "user_id": 1,
        "first_name": "Julie",
        "last_name": "Smith",
        "email": "admin@admin.com",
        "password": generate_password_hash("password", method="pbkdf2:sha256"),
        "role": "admin",
        "has_activated": True,
        "created_at": datetime.now(timezone.utc),
    }
]

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

# ---------- Email Validation Pattern ----------
EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$")


@app.context_processor
def inject_user():
    """
    Make the logged-in user's details (email & role) globally available
    to all templates.
    """
    email = session.get("user_email")

    # Find user (if logged in)
    if not email:
        return dict(email=None, role=None)

    user = get_user_by_email(email, REGISTERED_USERS)
    if not user:
        return dict(email=None, role=None)

    return dict(email=user["email"], role=user["role"])


# Route for the home page
@app.route("/")
def home():
    user_email = session.get("user_email")
    if not user_email:
        return redirect(url_for("login"))

    user = get_user_by_email(user_email, REGISTERED_USERS)

    if not user:
        return redirect(url_for("login"))

    return render_template("home.html", user=user, patients=PATIENTS)


# Route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        try:
            # ----- value checks -----
            if not (email and password):
                raise ValueError("Please enter both email and password.")

            # ----- Check if user exist -----
            user = find_user(email, password, REGISTERED_USERS)
            if not user:
                raise ValueError("Invalid email or password")

            # if the user hasn't activated their account yet
            if not user["has_activated"]:
                session["pending_activation_id"] = user["user_id"]
                flash("Please activate your account before continuing.", "info")
                return redirect(url_for("activate"))

            # Normal login flow
            session["user_id"] = user["user_id"]
            session["user_email"] = user["email"]
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


@app.route("/register", methods=["GET", "POST"])
def register():
    # Ensure only admins can access this page
    if session.get("user_role") != "admin":
        flash("Access denied: Only admins can register new users.", "danger")
        return redirect(url_for("home"))

    temp_password = str(secrets.token_hex(4))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").lower().strip()
        role = request.form.get("role", "").lower().strip()

        # Validate required fields
        if not (first_name and last_name and email and role):
            flash("All fields are required.", "warning")
            return render_template("register.html")

        user = get_user_by_email(email, REGISTERED_USERS)

        if user:
            flash("A user with that email already exists.", "danger")
            return render_template("register.html")

        # Add new user
        new_user = {
            "user_id": len(REGISTERED_USERS) + 1,
            "email": email,
            "password": generate_password_hash(temp_password, method="pbkdf2:sha256"),
            "has_activated": False,
            "role": role,
            "first_name": first_name,
            "last_name": last_name,
        }
        REGISTERED_USERS.append(new_user)

        flash(
            f"✅ {first_name} {last_name} registered successfully! Temp password: {temp_password}",
            "success",
        )

        print(REGISTERED_USERS)
        return redirect(url_for("home"))

    return render_template("register.html", temp_password=temp_password)


@app.route("/activate", methods=["GET", "POST"])
def activate():
    user_id = session.get("pending_activation_id")
    if not user_id:
        flash("No account pending activation.", "warning")
        return redirect(url_for("login"))

    # Find the user
    user = next((u for u in REGISTERED_USERS if u["user_id"] == user_id), None)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not new_password or not confirm_password:
            flash("Please fill in both password fields.", "warning")
            return render_template("activate.html", email=user["email"])

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("activate.html", email=user["email"])

        # Update password and mark account as activated
        user["password"] = generate_password_hash(new_password)
        user["has_activated"] = True
        session.pop("pending_activation_id", None)

        print(REGISTERED_USERS)

        flash("Account activated! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("activate.html", email=user["email"])


if __name__ == "__main__":
    app.run(debug=True, port=3000)
