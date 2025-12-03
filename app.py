from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from utils.config import Config
from models.initialize import initialize
from utils.decorators import login_required
from utils.current_user import get_current_user
from routes import admin_bp, auth_bp, clinician_bp

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Register Blueprints
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(clinician_bp, url_prefix="/clinicians")

initialize()


# Custom filter to format ISO UTC strings to human-readable dates
@app.template_filter("humanize_date")
def humanize_date(iso_string: str) -> str:
    """
    Converts ISO 8601 string to '30 Nov 2025, 10:31 PM' format.
    """
    dt = datetime.fromisoformat(iso_string)
    return dt.strftime("%d %b %Y, %I:%M %p")


# Context processor to inject user info into templates
@app.context_processor
def inject_user():
    """
    Make logged-in user's username and role name globally available
    to all templates.
    """
    current_user = get_current_user()

    if not current_user:
        return dict(username=None, role_name=None)

    return dict(username=current_user["username"], role_name=current_user["role_name"])


# GET: Handle the index page
@app.route("/", methods=["GET"])
@login_required
def index():
    current_user = get_current_user()

    if current_user and current_user["role_name"] == "admin":
        return redirect(url_for("admin.dashboard"))

    if current_user and current_user["role_name"] == "clinician":
        return redirect(url_for("clinician.dashboard"))
    return render_template("errors/404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=3000)
