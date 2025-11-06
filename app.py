import os
import re
from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

# set STROKE_APP_SECRET_KEY via environment variable
app.secret_key = os.environ.get("STROKE_APP_SECRET_KEY", "my_dev_secret_key")

# ---------- Simple in-memory storage ----------
REGISTERED_USERS = [
    {
        "email": "admin@admin.com",
        "password": "password",
        "created_at": datetime.now(timezone.utc),
    }
]

# ---------- Email Validation pattern ----------
EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$")


# Route for the home page
@app.route("/")
def home():
    return render_template("home.html", users=REGISTERED_USERS)


# Route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = (request.form.get("password") or "").strip()
        try:
            # ----- value checks -----
            if not email or not password:
                raise ValueError("All fields are required")

            # ----- Format checks -----
            if not EMAIL_PATTERN.fullmatch(email):
                raise ValueError("Invalid email")

            # ----- Length checks -----
            if len(email) > 100:
                raise ValueError("Email too long.")

            # ----- Check if user exist -----
            found = False
            for user in REGISTERED_USERS:
                if user["email"] == email and user["password"] == password:
                    found = True
                    break
            if not found:
                raise ValueError("User not found")

            flash(f"✅ Logged in successfully!", "success")
            return redirect(url_for("home"))

        except ValueError as e:
            flash(f"⚠ Validation error: {e}", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, port=3000)
