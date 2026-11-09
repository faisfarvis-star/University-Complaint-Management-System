from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import (BooleanField, PasswordField, SelectField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

from ..utils.constants import PRIORITIES, STATUSES


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me signed in")


class RegisterForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    registration_number = StringField("Registration number", validators=[DataRequired(), Length(max=30)])
    department = StringField("Department / programme", validators=[Optional(), Length(max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password", "Passwords must match.")])


class ComplaintForm(FlaskForm):
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired(), Length(min=5, max=150)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10, max=5000)])
    priority = SelectField("Priority", choices=[(p, p) for p in PRIORITIES], default="Medium")
    attachments = MultipleFileField("Supporting attachments (PDF, PNG, JPG, TXT, DOCX — max 5 MB each)")


class CommentForm(FlaskForm):
    message = TextAreaField("Add a comment", validators=[DataRequired(), Length(min=2, max=2000)])


class StatusForm(FlaskForm):
    new_status = SelectField("New status", choices=[(s, s) for s in STATUSES])
    remarks = TextAreaField("Note / reason", validators=[Optional(), Length(max=1000)])


class AssignForm(FlaskForm):
    staff_id = SelectField("Assign to", coerce=int, validators=[DataRequired()])
    remarks = StringField("Remarks (optional)", validators=[Optional(), Length(max=300)])


class ProfileForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    department = StringField("Department / programme", validators=[Optional(), Length(max=100)])


class PasswordForm(FlaskForm):
    current = PasswordField("Current password", validators=[DataRequired()])
    new = PasswordField("New password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Confirm new password", validators=[DataRequired(), EqualTo("new", "Passwords must match.")])


class StaffForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    department = StringField("Department", validators=[Optional(), Length(max=100)])
    password = PasswordField("Temporary password", validators=[DataRequired(), Length(min=8, max=128)])


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=80)])
    description = StringField("Description", validators=[Optional(), Length(max=255)])


class EmptyForm(FlaskForm):
    """CSRF-only form for simple POST actions."""
