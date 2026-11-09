from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..forms import LoginForm, RegisterForm
from ..services import ServiceError
from ..services.factory import auth_service
from ..utils.helpers import is_safe_url

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user, error = auth_service().authenticate(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember.data)
            nxt = request.args.get("next")
            return redirect(nxt if is_safe_url(nxt) else url_for("main.dashboard"))
        flash(error, "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            auth_service().register_student(form.full_name.data, form.email.data, form.password.data,
                                            form.registration_number.data, form.department.data)
        except ServiceError as exc:
            flash(str(exc), "danger")
        else:
            flash("Account created. You can now sign in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
