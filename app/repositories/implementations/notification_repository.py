from ...extensions import db
from ...models import Notification
from ..interfaces import NotificationRepository


class SqlAlchemyNotificationRepository(NotificationRepository):
    def create(self, notification):
        db.session.add(notification)
        db.session.commit()
        return notification

    def get_by_id(self, notification_id):
        return db.session.get(Notification, notification_id)

    def list_for_user(self, user_id, limit=100):
        return (Notification.query.filter_by(user_id=user_id)
                .order_by(Notification.created_at.desc(), Notification.id.desc()).limit(limit).all())

    def unread_count(self, user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    def mark_read(self, notification):
        notification.is_read = True
        db.session.commit()
        return notification

    def mark_all_read(self, user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
        db.session.commit()
