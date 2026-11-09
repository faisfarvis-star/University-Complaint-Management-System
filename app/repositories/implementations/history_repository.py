from ...extensions import db
from ...models import ComplaintHistory
from ..interfaces import ComplaintHistoryRepository


class SqlAlchemyComplaintHistoryRepository(ComplaintHistoryRepository):
    def create(self, entry):
        db.session.add(entry)
        db.session.commit()
        return entry

    def list_by_complaint(self, complaint_id):
        return (ComplaintHistory.query.filter_by(complaint_id=complaint_id)
                .order_by(ComplaintHistory.created_at, ComplaintHistory.id).all())
