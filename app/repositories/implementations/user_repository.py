from sqlalchemy import func

from ...extensions import db
from ...models import User
from ..interfaces import UserRepository


class SqlAlchemyUserRepository(UserRepository):
    def create(self, user):
        db.session.add(user)
        db.session.commit()
        return user

    def get_by_id(self, user_id):
        return db.session.get(User, user_id)

    def get_by_email(self, email):
        return User.query.filter(func.lower(User.email) == (email or "").strip().lower()).first()

    def get_by_registration_number(self, registration_number):
        return User.query.filter_by(registration_number=registration_number).first()

    def list_by_role(self, role, active_only=False):
        q = User.query.filter_by(role=role)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.order_by(User.full_name).all()

    def update(self, user):
        db.session.add(user)
        db.session.commit()
        return user

    def count_by_role(self, role):
        return User.query.filter_by(role=role).count()
