from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session
from datetime import timedelta
from config import Config
from models.bootstrap import bootstrap_once
from utils.decorators import login_required
from utils.current_user import get_current_user
from flask_wtf import CSRFProtect
from routes import admin_bp, auth_bp, clinician_bp

app = Flask(__name__)


# Secret key for signing/encrypting session cookie
app.config["SECRET_KEY"] = Config.SECRET_KEY

# Make session permanent and set expiration
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

# Secure cookie options
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# CSRF protection
csrf = CSRFProtect(app)

# Register Blueprints
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(clinician_bp, url_prefix="/clinicians")

bootstrap_once()


@app.before_request
def refresh_session():
    session.permanent = True


# Error 404 handler
@app.errorhandler(404)
def page_not_found(error):
    app.logger.warning(f"404 Not Found: {error}, Path: {request.path}")
    return render_template("errors/404.html"), 404


# Error 500 handler
@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(f"500 Internal Server Error: {error}, Path: {request.path}")
    return render_template("errors/500.html"), 500


@app.template_filter("humanize_date")
def humanize_date(iso_string: str) -> str:
    """
    Converts ISO 8601 string to human-readable dates format.
    """
    dt = datetime.fromisoformat(iso_string)
    return dt.strftime("%d %b %Y, %I:%M %p")


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
