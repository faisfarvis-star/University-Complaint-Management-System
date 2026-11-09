from ..extensions import db
from ..utils.constants import FINAL_STATUSES, PENDING
from ..utils.helpers import utcnow


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))


class Complaint(db.Model):
    __tablename__ = "complaints"
    __table_args__ = (
        db.Index("ix_complaints_student", "student_id"),
        db.Index("ix_complaints_staff", "assigned_staff_id"),
        db.Index("ix_complaints_status", "status"),
        db.Index("ix_complaints_created", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    complaint_number = db.Column(db.String(20), nullable=False, unique=True, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), nullable=False, default="Medium")
    status = db.Column(db.String(20), nullable=False, default=PENDING)
    resolution_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime)

    student = db.relationship("User", foreign_keys=[student_id])
    assigned_staff = db.relationship("User", foreign_keys=[assigned_staff_id])
    category = db.relationship("Category")
    history = db.relationship("ComplaintHistory", backref="complaint",
                              order_by="ComplaintHistory.created_at", cascade="all, delete-orphan")
    comments = db.relationship("ComplaintComment", backref="complaint",
                               order_by="ComplaintComment.created_at", cascade="all, delete-orphan")
    attachments = db.relationship("Attachment", backref="complaint", cascade="all, delete-orphan")

    def is_overdue(self, days=7):
        if self.status in FINAL_STATUSES or not self.created_at:
            return False
        return (utcnow() - self.created_at).days >= days


class ComplaintHistory(db.Model):
    __tablename__ = "complaint_history"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    user = db.relationship("User")


class ComplaintComment(db.Model):
    __tablename__ = "complaint_comments"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    user = db.relationship("User")


class Attachment(db.Model):
    __tablename__ = "attachments"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    uploaded_at = db.Column(db.DateTime, default=utcnow, nullable=False)
