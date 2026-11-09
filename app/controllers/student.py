from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..forms import ComplaintForm
from ..services import ServiceError
from ..services.factory import categories, complaint_service, stats_service
from ..utils.constants import ROLE_STUDENT
from ..utils.decorators import roles_required
from .filters import read_filters

bp = Blueprint("student", __name__, url_prefix="/student")


def _form():
    form = ComplaintForm()
    form.category_id.choices = [(c.id, c.name) for c in categories().list_all()]
    return form


@bp.route("/dashboard")
@roles_required(ROLE_STUDENT)
def dashboard():
    return render_template("student/dashboard.html", stats=stats_service().student_dashboard(current_user.id))


@bp.route("/complaints")
@roles_required(ROLE_STUDENT)
def my_complaints():
    filters = read_filters(request.args)
    return render_template("shared/complaint_list.html", title="My Complaints", scope="student",
                           complaints=complaint_service().list_for_user(current_user, filters),
                           filters=filters, categories=categories().list_all())


@bp.route("/complaints/new", methods=["GET", "POST"])
@roles_required(ROLE_STUDENT)
def submit():
    form = _form()
    if form.validate_on_submit():
        try:
            complaint = complaint_service().submit(current_user, form.category_id.data, form.title.data,
                                                   form.description.data, form.priority.data,
                                                   form.attachments.data)
            flash(f"Complaint {complaint.complaint_number} submitted.", "success")
            return redirect(url_for("main.complaint_detail", complaint_id=complaint.id))
        except ServiceError as exc:
            flash(str(exc), "danger")
    return render_template("student/complaint_form.html", form=form, editing=False)


@bp.route("/complaints/<int:complaint_id>/edit", methods=["GET", "POST"])
@roles_required(ROLE_STUDENT)
def edit(complaint_id):
    svc = complaint_service()
    try:
        complaint = svc.get_for_user(complaint_id, current_user)
        if not svc.can_edit(complaint, current_user):
            flash("Only pending, unassigned complaints can be edited.", "warning")
            return redirect(url_for("main.complaint_detail", complaint_id=complaint_id))
    except ServiceError as exc:
        from .main import _handle
        _handle(exc)
    form = _form() if request.method == "POST" else _form_from(complaint)
    if form.validate_on_submit():
        try:
            svc.update_pending(complaint_id, current_user, form.category_id.data, form.title.data,
                               form.description.data, form.priority.data)
            flash("Complaint updated.", "success")
            return redirect(url_for("main.complaint_detail", complaint_id=complaint_id))
        except ServiceError as exc:
            flash(str(exc), "danger")
    return render_template("student/complaint_form.html", form=form, editing=True, complaint=complaint)


def _form_from(complaint):
    form = ComplaintForm(obj=complaint)
    form.category_id.choices = [(c.id, c.name) for c in categories().list_all()]
    return form
