"""Business rules for complaints. Depends only on repository interfaces."""
from ..models import (Attachment, AuditLog, Complaint, ComplaintComment, ComplaintHistory,
                      Notification)
from ..utils.constants import (ASSIGNED, CLOSED, PENDING, PRIORITIES, REOPENED, RESOLVED,
                               ROLE_ADMIN, ROLE_STAFF, ROLE_STUDENT, STATUSES, TRANSITIONS)
from ..utils.files import UploadPolicy, save_upload, validate_upload
from ..utils.helpers import utcnow
from .exceptions import InvalidTransition, NotFound, PermissionDenied, ValidationError


class ComplaintService:
    def __init__(self, complaints, history, notifications, users, categories,
                 comments=None, attachments=None, audit=None, upload_policy=None):
        self.complaints = complaints
        self.history = history
        self.notifications = notifications
        self.users = users
        self.categories = categories
        self.comments = comments
        self.attachments = attachments
        self.audit = audit
        self.policy = upload_policy or UploadPolicy()

    # ---------- helpers ----------
    def _audit(self, actor, action, entity_id):
        if self.audit:
            self.audit.create(AuditLog(actor_id=actor.id, action=action,
                                       entity_type="complaint", entity_id=entity_id))

    def _notify(self, user_id, title, message, complaint_id):
        if user_id:
            self.notifications.create(Notification(user_id=user_id, title=title, message=message,
                                                   complaint_id=complaint_id))

    def _notify_admins(self, title, message, complaint_id, exclude_id=None):
        for admin in self.users.list_by_role(ROLE_ADMIN, active_only=True):
            if admin.id != exclude_id:
                self._notify(admin.id, title, message, complaint_id)

    def _record(self, complaint, actor, old, new, remarks):
        self.history.create(ComplaintHistory(complaint_id=complaint.id, changed_by=actor.id,
                                             old_status=old, new_status=new, remarks=remarks))

    @staticmethod
    def can_access(complaint, user):
        if user.role == ROLE_ADMIN:
            return True
        if user.role == ROLE_STUDENT:
            return complaint.student_id == user.id
        if user.role == ROLE_STAFF:
            return complaint.assigned_staff_id == user.id
        return False

    def get_for_user(self, complaint_id, user):
        complaint = self.complaints.get_by_id(complaint_id)
        if complaint is None:
            raise NotFound("Complaint not found.")
        if not self.can_access(complaint, user):
            raise PermissionDenied("You do not have access to this complaint.")
        return complaint

    def allowed_statuses(self, complaint, user):
        """Statuses this user may move the complaint to via the status form."""
        if not self.can_access(complaint, user):
            return []
        return [new for (old, new), roles in TRANSITIONS.items()
                if old == complaint.status and user.role in roles and new != ASSIGNED]

    def can_edit(self, complaint, user):
        return (user.role == ROLE_STUDENT and complaint.student_id == user.id
                and complaint.status == PENDING and complaint.assigned_staff_id is None)

    def _validate_fields(self, category_id, title, description, priority):
        title, description = (title or "").strip(), (description or "").strip()
        if not 5 <= len(title) <= 150:
            raise ValidationError("Title must be between 5 and 150 characters.")
        if not 10 <= len(description) <= 5000:
            raise ValidationError("Description must be between 10 and 5000 characters.")
        if priority not in PRIORITIES:
            raise ValidationError("Invalid priority.")
        if not category_id or self.categories.get_by_id(category_id) is None:
            raise ValidationError("Please select a valid category.")
        return title, description

    # ---------- use cases ----------
    def submit(self, student, category_id, title, description, priority, files=None):
        if student.role != ROLE_STUDENT:
            raise PermissionDenied("Only students can submit complaints.")
        title, description = self._validate_fields(category_id, title, description, priority)
        files = [f for f in (files or []) if f and f.filename]
        for f in files:
            error = validate_upload(f, self.policy)
            if error:
                raise ValidationError(error)
        complaint = self.complaints.create(Complaint(
            complaint_number=self.complaints.next_complaint_number(), student_id=student.id,
            category_id=category_id, title=title, description=description,
            priority=priority, status=PENDING))
        self._record(complaint, student, None, PENDING, "Complaint submitted")
        for f in files:
            original, stored = save_upload(f, self.policy)
            self.attachments.create(Attachment(complaint_id=complaint.id,
                                               original_filename=original, stored_filename=stored))
        self._notify(student.id, "Complaint submitted",
                     f"{complaint.complaint_number} was received and is pending review.", complaint.id)
        self._notify_admins("New complaint", f"{complaint.complaint_number}: {title}", complaint.id)
        self._audit(student, "complaint submitted", complaint.id)
        return complaint

    def update_pending(self, complaint_id, student, category_id, title, description, priority):
        complaint = self.get_for_user(complaint_id, student)
        if not self.can_edit(complaint, student):
            raise InvalidTransition("Only pending, unassigned complaints can be edited.")
        title, description = self._validate_fields(category_id, title, description, priority)
        complaint.category_id, complaint.title = category_id, title
        complaint.description, complaint.priority = description, priority
        complaint.updated_at = utcnow()
        self.complaints.update(complaint)
        self._audit(student, "complaint edited", complaint.id)
        return complaint

    def assign(self, complaint_id, staff_id, actor, remarks=""):
        if actor.role != ROLE_ADMIN:
            raise PermissionDenied("Only administrators can assign complaints.")
        complaint = self.complaints.get_by_id(complaint_id)
        if complaint is None:
            raise NotFound("Complaint not found.")
        staff = self.users.get_by_id(staff_id)
        if not staff or staff.role != ROLE_STAFF or not staff.is_active:
            raise ValidationError("Select an active staff member.")
        old = complaint.status
        if old not in (PENDING, ASSIGNED, REOPENED):
            raise InvalidTransition("Only pending, assigned or reopened complaints can be (re)assigned.")
        complaint.assigned_staff_id = staff.id
        complaint.status = ASSIGNED
        complaint.updated_at = utcnow()
        self.complaints.update(complaint)
        verb = "Reassigned" if old == ASSIGNED else "Assigned"
        note = (remarks or "").strip() or f"{verb} to {staff.full_name}"
        self._record(complaint, actor, old, ASSIGNED, note)
        self._notify(staff.id, "New assignment",
                     f"{complaint.complaint_number} has been assigned to you.", complaint.id)
        self._notify(complaint.student_id, "Complaint assigned",
                     f"{complaint.complaint_number} was assigned to {staff.full_name}.", complaint.id)
        self._audit(actor, f"complaint {verb.lower()} to {staff.email}", complaint.id)
        return complaint

    def change_status(self, complaint_id, new_status, actor, remarks=""):
        complaint = self.get_for_user(complaint_id, actor)
        if new_status not in STATUSES:
            raise ValidationError("Unknown status.")
        if new_status == ASSIGNED:
            raise InvalidTransition("Use the assignment action to assign a complaint.")
        old = complaint.status
        roles = TRANSITIONS.get((old, new_status))
        if not roles or actor.role not in roles:
            raise InvalidTransition(f"You cannot change a complaint from '{old}' to '{new_status}'.")
        remarks = (remarks or "").strip()
        if new_status in (RESOLVED, REOPENED) and not remarks:
            raise ValidationError("A resolution note / reopen reason is required.")
        complaint.status = new_status
        complaint.updated_at = utcnow()
        if new_status == RESOLVED:
            complaint.resolved_at = utcnow()
            complaint.resolution_notes = remarks
        elif new_status == REOPENED:
            complaint.resolved_at = None
        self.complaints.update(complaint)
        self._record(complaint, actor, old, new_status, remarks or None)
        num = complaint.complaint_number
        if actor.id != complaint.student_id:
            self._notify(complaint.student_id, f"Complaint {new_status.lower()}",
                         f"{num} is now '{new_status}'.", complaint.id)
        if new_status == RESOLVED:
            self._notify_admins("Resolution awaiting verification", f"{num} was marked resolved.",
                                complaint.id, exclude_id=actor.id)
        if new_status == REOPENED:
            if complaint.assigned_staff_id and complaint.assigned_staff_id != actor.id:
                self._notify(complaint.assigned_staff_id, "Complaint reopened",
                             f"{num} was reopened: {remarks}", complaint.id)
            self._notify_admins("Complaint reopened", f"{num} was reopened.", complaint.id,
                                exclude_id=actor.id)
        self._audit(actor, f"status {old} -> {new_status}", complaint.id)
        return complaint

    def add_comment(self, complaint_id, actor, message):
        complaint = self.get_for_user(complaint_id, actor)
        message = (message or "").strip()
        if not 2 <= len(message) <= 2000:
            raise ValidationError("Comment must be between 2 and 2000 characters.")
        comment = self.comments.create(ComplaintComment(complaint_id=complaint.id,
                                                        user_id=actor.id, message=message))
        num = complaint.complaint_number
        if actor.id == complaint.student_id:
            targets = [complaint.assigned_staff_id] if complaint.assigned_staff_id else \
                [a.id for a in self.users.list_by_role(ROLE_ADMIN, active_only=True)]
            for uid in targets:
                self._notify(uid, "New student comment", f"{num}: {message[:80]}", complaint.id)
        else:
            self._notify(complaint.student_id, "New response", f"{num}: {message[:80]}", complaint.id)
        self._audit(actor, "comment added", complaint.id)
        return comment

    def list_for_user(self, user, filters=None):
        if user.role == ROLE_ADMIN:
            return self.complaints.search(filters)
        if user.role == ROLE_STUDENT:
            return self.complaints.search(filters, student_id=user.id)
        return self.complaints.search(filters, staff_id=user.id)
