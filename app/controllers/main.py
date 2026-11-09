import os

from flask import (Blueprint, abort, current_app, flash, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_login import current_user, login_required

from ..forms import (AssignForm, CommentForm, EmptyForm, PasswordForm, ProfileForm, StatusForm)
from ..repositories.implementations import (SqlAlchemyAttachmentRepository,
                                            SqlAlchemyNotificationRepository)
from ..services import NotFound, PermissionDenied, ServiceError
from ..services.factory import auth_service, complaint_service, users
from ..utils.constants import ROLE_ADMIN, ROLE_STAFF, ROLE_STUDENT

bp = Blueprint("main", __name__)
HOME = {ROLE_ADMIN: "admin.dashboard", ROLE_STUDENT: "student.dashboard", ROLE_STAFF: "staff.dashboard"}


def _handle(exc):
    """Translate service errors into HTTP responses / flash messages."""
    if isinstance(exc, PermissionDenied):
        abort(403)
    if isinstance(exc, NotFound):
        abort(404)
    flash(str(exc), "danger")


@bp.route("/")
def index():
    return redirect(url_for("main.dashboard" if current_user.is_authenticated else "auth.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    return redirect(url_for(HOME[current_user.role]))


@bp.route("/complaints/<int:complaint_id>")
@login_required
def complaint_detail(complaint_id):
    svc = complaint_service()
    try:
        complaint = svc.get_for_user(complaint_id, current_user)
    except (PermissionDenied, NotFound) as exc:
        _handle(exc)
    status_form = StatusForm()
    allowed = svc.allowed_statuses(complaint, current_user)
    status_form.new_status.choices = [(s, s) for s in allowed]
    assign_form = AssignForm()
    if current_user.role == ROLE_ADMIN:
        assign_form.staff_id.choices = [(s.id, f"{s.full_name} ({s.department or 'Staff'})")
                                        for s in users().list_by_role(ROLE_STAFF, active_only=True)]
    return render_template("shared/complaint_detail.html", complaint=complaint,
                           status_form=status_form, allowed=allowed, assign_form=assign_form,
                           comment_form=CommentForm(), can_edit=svc.can_edit(complaint, current_user))


@bp.route("/complaints/<int:complaint_id>/comment", methods=["POST"])
@login_required
def add_comment(complaint_id):
    form = CommentForm()
    if form.validate_on_submit():
        try:
            complaint_service().add_comment(complaint_id, current_user, form.message.data)
            flash("Comment added.", "success")
        except ServiceError as exc:
            _handle(exc)
    else:
        flash("Comment must be between 2 and 2000 characters.", "danger")
    return redirect(url_for("main.complaint_detail", complaint_id=complaint_id))


@bp.route("/complaints/<int:complaint_id>/status", methods=["POST"])
@login_required
def change_status(complaint_id):
    svc = complaint_service()
    form = StatusForm()
    try:
        complaint = svc.get_for_user(complaint_id, current_user)
        form.new_status.choices = [(s, s) for s in svc.allowed_statuses(complaint, current_user)]
        if form.validate_on_submit():
            svc.change_status(complaint_id, form.new_status.data, current_user, form.remarks.data)
            flash(f"Status updated to {form.new_status.data}.", "success")
        else:
            flash("Please choose a valid status.", "danger")
    except ServiceError as exc:
        _handle(exc)
    return redirect(url_for("main.complaint_detail", complaint_id=complaint_id))


@bp.route("/complaints/<int:complaint_id>/assign", methods=["POST"])
@login_required
def assign(complaint_id):
    if current_user.role != ROLE_ADMIN:
        abort(403)
    form = AssignForm()
    form.staff_id.choices = [(s.id, s.full_name) for s in users().list_by_role(ROLE_STAFF, active_only=True)]
    if form.validate_on_submit():
        try:
            complaint_service().assign(complaint_id, form.staff_id.data, current_user, form.remarks.data)
            flash("Complaint assigned.", "success")
        except ServiceError as exc:
            _handle(exc)
    else:
        flash("Select an active staff member.", "danger")
    return redirect(request.form.get("next_url") if request.form.get("next_url", "").startswith("/")
                    else url_for("main.complaint_detail", complaint_id=complaint_id))


@bp.route("/attachments/<int:attachment_id>")
@login_required
def download_attachment(attachment_id):
    attachment = SqlAlchemyAttachmentRepository().get_by_id(attachment_id)
    if attachment is None:
        abort(404)
    try:
        complaint_service().get_for_user(attachment.complaint_id, current_user)  # permission check
    except ServiceError as exc:
        _handle(exc)
    return send_from_directory(os.path.abspath(current_app.config["UPLOAD_FOLDER"]),
                               attachment.stored_filename, as_attachment=True,
                               download_name=attachment.original_filename)


@bp.route("/notifications")
@login_required
def notifications():
    items = SqlAlchemyNotificationRepository().list_for_user(current_user.id)
    return render_template("shared/notifications.html", items=items, form=EmptyForm())


@bp.route("/notifications/<int:notification_id>/open", methods=["POST"])
@login_required
def open_notification(notification_id):
    repo = SqlAlchemyNotificationRepository()
    note = repo.get_by_id(notification_id)
    if note is None or note.user_id != current_user.id:
        abort(404)
    repo.mark_read(note)
    if note.complaint_id:
        return redirect(url_for("main.complaint_detail", complaint_id=note.complaint_id))
    return redirect(url_for("main.notifications"))


@bp.route("/notifications/read-all", methods=["POST"])
@login_required
def read_all_notifications():
    SqlAlchemyNotificationRepository().mark_all_read(current_user.id)
    flash("All notifications marked as read.", "success")
    return redirect(url_for("main.notifications"))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        try:
            auth_service().update_profile(current_user, form.full_name.data, form.department.data)
            flash("Profile updated.", "success")
            return redirect(url_for("main.profile"))
        except ServiceError as exc:
            flash(str(exc), "danger")
    return render_template("shared/profile.html", form=form)


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = PasswordForm()
    if form.validate_on_submit():
        try:
            auth_service().change_password(current_user, form.current.data, form.new.data)
            flash("Password changed.", "success")
            return redirect(url_for("main.settings"))
        except ServiceError as exc:
            flash(str(exc), "danger")
    return render_template("shared/settings.html", form=form)
