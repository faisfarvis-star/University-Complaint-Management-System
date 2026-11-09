from flask import Blueprint, render_template, request
from flask_login import current_user

from ..services.factory import categories, complaint_service, stats_service
from ..utils.constants import ACTIVE_STATUSES, FINAL_STATUSES, ROLE_STAFF
from ..utils.decorators import roles_required
from .filters import read_filters

bp = Blueprint("staff", __name__, url_prefix="/staff")


@bp.route("/dashboard")
@roles_required(ROLE_STAFF)
def dashboard():
    return render_template("staff/dashboard.html", stats=stats_service().staff_dashboard(current_user.id))


@bp.route("/complaints")
@roles_required(ROLE_STAFF)
def assigned():
    filters = read_filters(request.args)
    if "status" not in filters:
        filters["statuses"] = list(ACTIVE_STATUSES)
    return render_template("shared/complaint_list.html", title="My Assigned Complaints", scope="staff",
                           complaints=complaint_service().list_for_user(current_user, filters),
                           filters=filters, categories=categories().list_all())


@bp.route("/completed")
@roles_required(ROLE_STAFF)
def completed():
    filters = read_filters(request.args)
    filters.pop("status", None)
    filters["statuses"] = list(FINAL_STATUSES)
    return render_template("shared/complaint_list.html", title="Completed Assignments", scope="staff",
                           complaints=complaint_service().list_for_user(current_user, filters),
                           filters=filters, categories=categories().list_all())
