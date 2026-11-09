from sqlalchemy import func

from ...extensions import db
from ...models import Category, Complaint
from ..interfaces import CategoryRepository


class SqlAlchemyCategoryRepository(CategoryRepository):
    def create(self, category):
        db.session.add(category)
        db.session.commit()
        return category

    def get_by_id(self, category_id):
        return db.session.get(Category, category_id)

    def get_by_name(self, name):
        return Category.query.filter(func.lower(Category.name) == (name or "").strip().lower()).first()

    def list_all(self):
        return Category.query.order_by(Category.name).all()

    def update(self, category):
        db.session.add(category)
        db.session.commit()
        return category

    def delete(self, category):
        db.session.delete(category)
        db.session.commit()

    def complaint_count(self, category_id):
        return Complaint.query.filter_by(category_id=category_id).count()
