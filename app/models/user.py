from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..utils.constants import ROLE_ADMIN, ROLE_STAFF, ROLE_STUDENT
from ..utils.helpers import utcnow


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    registration_number = db.Column(db.String(30), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def is_staff_member(self):
        return self.role == ROLE_STAFF

    @property
    def is_student(self):
        return self.role == ROLE_STUDENT

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
