from flask import Blueprint, render_template
from utils.decorators import login_required, auditor_required
from models.auditor.auditor_model import get_logs


auditor_bp = Blueprint("auditor", __name__)


# auditor routes
@auditor_bp.route("/dashboard", methods=["GET"])
@login_required
@auditor_required
def dashboard():
    logs = get_logs()
    return render_template("auditor/dashboard.html", logs=logs)
