from ...extensions import db
from ...models import Attachment, AuditLog, ComplaintComment
from ..interfaces import AttachmentRepository, AuditLogRepository, CommentRepository


class SqlAlchemyCommentRepository(CommentRepository):
    def create(self, comment):
        db.session.add(comment)
        db.session.commit()
        return comment

    def list_by_complaint(self, complaint_id):
        return (ComplaintComment.query.filter_by(complaint_id=complaint_id)
                .order_by(ComplaintComment.created_at, ComplaintComment.id).all())


class SqlAlchemyAttachmentRepository(AttachmentRepository):
    def create(self, attachment):
        db.session.add(attachment)
        db.session.commit()
        return attachment

    def get_by_id(self, attachment_id):
        return db.session.get(Attachment, attachment_id)

    def list_by_complaint(self, complaint_id):
        return Attachment.query.filter_by(complaint_id=complaint_id).all()


class SqlAlchemyAuditLogRepository(AuditLogRepository):
    def create(self, entry):
        db.session.add(entry)
        db.session.commit()
        return entry

    def list_recent(self, limit=200):
        return AuditLog.query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(limit).all()
