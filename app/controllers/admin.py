from flask import (Blueprint, Response, abort, flash, redirect, render_template, request, url_for)
from flask_login import current_user

from ..forms import AssignForm, CategoryForm, EmptyForm, StaffForm
from ..models import AuditLog, Category
from ..repositories.implementations import SqlAlchemyAuditLogRepository
from ..services import ServiceError
from ..services.factory import auth_service, categories, complaint_service, stats_service, users
from ..services.report_service import complaints_csv
from ..utils.constants import (ACTIVE_STATUSES, ROLE_ADMIN, ROLE_STAFF, ROLE_STUDENT)
from ..utils.decorators import roles_required
from .filters import read_filters

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/dashboard")
@roles_required(ROLE_ADMIN)
def dashboard():
    return render_template("admin/dashboard.html", stats=stats_service().admin_dashboard())


@bp.route("/complaints")
@roles_required(ROLE_ADMIN)
def complaints():
    filters = read_filters(request.args)
    return render_template("shared/complaint_list.html", title="All Complaints", scope="admin",
                           complaints=complaint_service().list_for_user(current_user, filters),
                           filters=filters, categories=categories().list_all())


@bp.route("/reports/complaints.csv")
@roles_required(ROLE_ADMIN)
def export_csv():
    items = complaint_service().list_for_user(current_user, read_filters(request.args))
    SqlAlchemyAuditLogRepository().create(AuditLog(actor_id=current_user.id, action="CSV report exported",
                                                   entity_type="report", entity_id=None))
    return Response(complaints_csv(items), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=complaints_report.csv"})


@bp.route("/assignments")
@roles_required(ROLE_ADMIN)
def assignments():
    items = complaint_service().complaints.search({"statuses": list(ACTIVE_STATUSES) + ["Pending"]})
    form = AssignForm()
    staff = users().list_by_role(ROLE_STAFF, active_only=True)
    return render_template("admin/assignments.html", complaints=items, staff=staff, form=form)


def _user_list(role, title):
    return render_template("admin/users.html", title=title, role=role,
                           people=users().list_by_role(role), form=EmptyForm())


@bp.route("/students")
@roles_required(ROLE_ADMIN)
def students():
    return _user_list(ROLE_STUDENT, "Student Accounts")


@bp.route("/staff")
@roles_required(ROLE_ADMIN)
def staff():
    return _user_list(ROLE_STAFF, "Staff Accounts")


@bp.route("/staff/new", methods=["GET", "POST"])
@roles_required(ROLE_ADMIN)
def new_staff():
    form = StaffForm()
    if form.validate_on_submit():
        try:
            auth_service().create_staff(current_user, form.full_name.data, form.email.data,
                                        form.password.data, form.department.data)
            flash("Staff account created.", "success")
            return redirect(url_for("admin.staff"))
        except ServiceError as exc:
            flash(str(exc), "danger")
    return render_template("admin/staff_form.html", form=form)


@bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@roles_required(ROLE_ADMIN)
def toggle_user(user_id):
    target = users().get_by_id(user_id)
    if target is None:
        abort(404)
    try:
        auth_service().set_active(current_user, user_id, not target.is_active)
        flash(f"Account {'activated' if target.is_active else 'deactivated'}.", "success")
    except ServiceError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.students" if target.role == ROLE_STUDENT else "admin.staff"))


@bp.route("/categories", methods=["GET", "POST"])
@roles_required(ROLE_ADMIN)
def manage_categories():
    form = CategoryForm()
    repo = categories()
    if form.validate_on_submit():
        if repo.get_by_name(form.name.data):
            flash("A category with this name already exists.", "danger")
        else:
            repo.create(Category(name=form.name.data.strip(), description=(form.description.data or "").strip()))
            flash("Category added.", "success")
            return redirect(url_for("admin.manage_categories"))
    rows = [(c, repo.complaint_count(c.id)) for c in repo.list_all()]
    return render_template("admin/categories.html", form=form, rows=rows, empty=EmptyForm())


@bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@roles_required(ROLE_ADMIN)
def edit_category(category_id):
    repo = categories()
    category = repo.get_by_id(category_id) or abort(404)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        other = repo.get_by_name(form.name.data)
        if other and other.id != category.id:
            flash("A category with this name already exists.", "danger")
        else:
            category.name = form.name.data.strip()
            category.description = (form.description.data or "").strip()
            repo.update(category)
            flash("Category updated.", "success")
            return redirect(url_for("admin.manage_categories"))
    return render_template("admin/category_edit.html", form=form, category=category)


@bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@roles_required(ROLE_ADMIN)
def delete_category(category_id):
    repo = categories()
    category = repo.get_by_id(category_id) or abort(404)
    if repo.complaint_count(category_id):
        flash("This category is used by complaints and cannot be deleted.", "danger")
    else:
        repo.delete(category)
        flash("Category deleted.", "success")
    return redirect(url_for("admin.manage_categories"))


@bp.route("/audit")
@roles_required(ROLE_ADMIN)
def audit():
    return render_template("admin/audit.html", logs=SqlAlchemyAuditLogRepository().list_recent(200))
