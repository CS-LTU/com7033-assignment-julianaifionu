import os
import re
from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from utils.auth import get_user_by_email

app = Flask(__name__)

# set STROKE_APP_SECRET_KEY via environment variable
app.secret_key = os.environ.get("STROKE_APP_SECRET_KEY", "my_dev_secret_key")

# ---------- Simple in-memory storage ----------
REGISTERED_USERS = [
    {
        "user_id": 1,
        "email": "admin@admin.com",
        "password": generate_password_hash("password1", method="pbkdf2:sha256"),
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
    },
    {
        "user_id": 2,
        "email": "doctor@hospital.com",
        "password": generate_password_hash("password2", method="pbkdf2:sha256"),
        "role": "doctor",
        "created_at": datetime.now(timezone.utc),
    },
    {
        "user_id": 3,
        "email": "nurse@hospital.com",
        "password": generate_password_hash("password3", method="pbkdf2:sha256"),
        "role": "nurse",
        "created_at": datetime.now(timezone.utc),
    },
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
    user_email = session.get("user_email")

    # Find user (if logged in)
    found_user = None
    if user_email:
        for user in REGISTERED_USERS:
            if user["email"] == user_email:
                found_user = user
                break

    if not found_user:
        return dict(email=None, role=None)

    return dict(email=found_user["email"], role=found_user.get("role"))


# Route for the home page
@app.route("/")
def home():
    user_email = session.get("user_email")
    if not user_email:
        return redirect(url_for("login"))

    found_user = None
    for user in REGISTERED_USERS:
        if user["email"] == user_email:
            found_user = user
            break

    if not found_user:
        return redirect(url_for("login"))

    return render_template("home.html", user=found_user, patients=PATIENTS)


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
            user = get_user_by_email(email, password, REGISTERED_USERS)
            if not user:
                raise ValueError("Invalid email or password")

            session["user_id"] = user["user_id"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]

            flash(f"✅ Logged in successfully!", "success")
            return redirect(url_for("home"))

        except ValueError as e:
            flash(f"⚠ Validation error: {e}", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, port=3000)
