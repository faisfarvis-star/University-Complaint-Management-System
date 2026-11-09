import re

from ..models import User
from ..utils.constants import ROLE_ADMIN, ROLE_STAFF, ROLE_STUDENT
from .exceptions import PermissionDenied, ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _check_password_strength(pw):
    if len(pw or "") < 8:
        raise ValidationError("Password must be at least 8 characters.")
    if not (any(c.isalpha() for c in pw) and any(c.isdigit() for c in pw)):
        raise ValidationError("Password must contain letters and numbers.")


class AuthService:
    def __init__(self, users, audit=None):
        self.users = users
        self.audit = audit

    def _log(self, actor_id, action, entity_id):
        if self.audit:
            from ..models import AuditLog
            self.audit.create(AuditLog(actor_id=actor_id, action=action, entity_type="user", entity_id=entity_id))

    def _create(self, role, full_name, email, password, department=None, registration_number=None):
        full_name = (full_name or "").strip()
        email = (email or "").strip().lower()
        if not full_name:
            raise ValidationError("Full name is required.")
        if not EMAIL_RE.match(email):
            raise ValidationError("A valid email address is required.")
        _check_password_strength(password)
        if self.users.get_by_email(email):
            raise ValidationError("An account with this email already exists.")
        reg = (registration_number or "").strip() or None
        if reg and self.users.get_by_registration_number(reg):
            raise ValidationError("This registration number is already registered.")
        user = User(full_name=full_name, email=email, role=role,
                    department=(department or "").strip() or None, registration_number=reg)
        user.set_password(password)
        return self.users.create(user)

    def register_student(self, full_name, email, password, registration_number, department=None):
        """Public registration: the role is always 'student' (never taken from input)."""
        if not (registration_number or "").strip():
            raise ValidationError("Registration number is required for students.")
        user = self._create(ROLE_STUDENT, full_name, email, password, department, registration_number)
        self._log(user.id, "student registered", user.id)
        return user

    def create_staff(self, actor, full_name, email, password, department=None):
        if actor.role != ROLE_ADMIN:
            raise PermissionDenied("Only administrators can create staff accounts.")
        user = self._create(ROLE_STAFF, full_name, email, password, department)
        self._log(actor.id, f"staff account created ({user.email})", user.id)
        return user

    def authenticate(self, email, password):
        """Returns (user, error). Same message for unknown user / wrong password."""
        user = self.users.get_by_email(email)
        if not user or not user.check_password(password or ""):
            return None, "Invalid email or password."
        if not user.is_active:
            return None, "This account has been deactivated. Contact the administrator."
        return user, None

    def set_active(self, actor, user_id, active):
        if actor.role != ROLE_ADMIN:
            raise PermissionDenied("Only administrators can manage accounts.")
        user = self.users.get_by_id(user_id)
        if not user or user.role == ROLE_ADMIN:
            raise ValidationError("This account cannot be changed.")
        user.is_active = bool(active)
        self.users.update(user)
        self._log(actor.id, f"account {'activated' if active else 'deactivated'} ({user.email})", user.id)
        return user

    def update_profile(self, user, full_name, department):
        full_name = (full_name or "").strip()
        if not full_name:
            raise ValidationError("Full name is required.")
        user.full_name = full_name
        user.department = (department or "").strip() or None
        return self.users.update(user)

    def change_password(self, user, current, new):
        if not user.check_password(current or ""):
            raise ValidationError("Current password is incorrect.")
        _check_password_strength(new)
        user.set_password(new)
        self.users.update(user)
        self._log(user.id, "password changed", user.id)
