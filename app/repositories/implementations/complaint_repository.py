from collections import Counter
from datetime import timedelta

from sqlalchemy import func, or_

from ...extensions import db
from ...models import Category, Complaint, User
from ...utils.constants import (ACTIVE_STATUSES, FINAL_STATUSES, PRIORITIES, ROLE_STAFF,
                                STATUSES)
from ...utils.helpers import utcnow
from ..interfaces import ComplaintRepository


class SqlAlchemyComplaintRepository(ComplaintRepository):
    # ---- basic CRUD -------------------------------------------------
    def create(self, complaint):
        db.session.add(complaint)
        db.session.commit()
        return complaint

    def get_by_id(self, complaint_id):
        return db.session.get(Complaint, complaint_id)

    def update(self, complaint):
        db.session.add(complaint)
        db.session.commit()
        return complaint

    def list_by_student(self, student_id):
        return self.search(student_id=student_id)

    def list_by_staff(self, staff_id):
        return self.search(staff_id=staff_id)

    def next_complaint_number(self):
        last = db.session.query(func.max(Complaint.id)).scalar() or 0
        return f"UCM-{utcnow().year}-{last + 1:04d}"

    # ---- querying ---------------------------------------------------
    @staticmethod
    def _scope(q, student_id=None, staff_id=None):
        if student_id is not None:
            q = q.filter(Complaint.student_id == student_id)
        if staff_id is not None:
            q = q.filter(Complaint.assigned_staff_id == staff_id)
        return q

    def search(self, filters=None, student_id=None, staff_id=None):
        f = filters or {}
        q = self._scope(Complaint.query, student_id, staff_id)
        if f.get("q"):
            like = f"%{f['q'].strip()}%"
            q = q.filter(or_(Complaint.title.ilike(like), Complaint.description.ilike(like),
                             Complaint.complaint_number.ilike(like)))
        if f.get("category_id"):
            q = q.filter(Complaint.category_id == f["category_id"])
        if f.get("priority"):
            q = q.filter(Complaint.priority == f["priority"])
        if f.get("status"):
            q = q.filter(Complaint.status == f["status"])
        if f.get("statuses"):
            q = q.filter(Complaint.status.in_(f["statuses"]))
        if f.get("date_from"):
            q = q.filter(Complaint.created_at >= f["date_from"])
        if f.get("date_to"):
            q = q.filter(Complaint.created_at < f["date_to"] + timedelta(days=1))
        if f.get("overdue"):
            cutoff = utcnow() - timedelta(days=f.get("overdue_days", 7))
            q = q.filter(Complaint.status.notin_(FINAL_STATUSES), Complaint.created_at <= cutoff)
        return q.order_by(Complaint.created_at.desc(), Complaint.id.desc()).all()

    def recent(self, limit=5, student_id=None, staff_id=None):
        q = self._scope(Complaint.query, student_id, staff_id)
        return q.order_by(Complaint.created_at.desc(), Complaint.id.desc()).limit(limit).all()

    def list_overdue(self, days=7):
        return self.search({"overdue": True, "overdue_days": days})

    # ---- statistics -------------------------------------------------
    def count_by_status(self, student_id=None, staff_id=None):
        q = db.session.query(Complaint.status, func.count(Complaint.id))
        q = self._scope(q, student_id, staff_id).group_by(Complaint.status)
        result = {s: 0 for s in STATUSES}
        result.update(dict(q.all()))
        return result

    def count_by_priority(self):
        rows = dict(db.session.query(Complaint.priority, func.count(Complaint.id))
                    .group_by(Complaint.priority).all())
        return {p: rows.get(p, 0) for p in PRIORITIES}

    def count_by_category(self):
        rows = (db.session.query(Category.name, func.count(Complaint.id))
                .outerjoin(Complaint, Complaint.category_id == Category.id)
                .group_by(Category.id).order_by(Category.name).all())
        return {name: count for name, count in rows}

    def monthly_trend(self, months=6):
        today = utcnow()
        keys = []
        y, m = today.year, today.month
        for _ in range(months):
            keys.append((y, m))
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        keys.reverse()
        start = today.replace(year=keys[0][0], month=keys[0][1], day=1, hour=0, minute=0, second=0, microsecond=0)
        created = [c for (c,) in db.session.query(Complaint.created_at).filter(Complaint.created_at >= start)]
        counter = Counter((c.year, c.month) for c in created)
        return [{"label": f"{y}-{m:02d}", "count": counter.get((y, m), 0)} for y, m in keys]

    def staff_performance(self):
        staff = User.query.filter_by(role=ROLE_STAFF).order_by(User.full_name).all()
        rows = Complaint.query.filter(Complaint.assigned_staff_id.isnot(None)).all()
        result = []
        for s in staff:
            mine = [c for c in rows if c.assigned_staff_id == s.id]
            done = [c for c in mine if c.status in FINAL_STATUSES]
            hours = [(c.resolved_at - c.created_at).total_seconds() / 3600
                     for c in done if c.resolved_at and c.created_at]
            result.append({
                "staff_id": s.id, "name": s.full_name, "assigned": len(mine),
                "active": len([c for c in mine if c.status in ACTIVE_STATUSES]),
                "resolved": len(done),
                "rate": round(100 * len(done) / len(mine)) if mine else 0,
                "avg_hours": round(sum(hours) / len(hours), 1) if hours else None,
            })
        return result
