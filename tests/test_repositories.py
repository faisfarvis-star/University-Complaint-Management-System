import pytest

from app.models import Complaint, Notification
from app.repositories.implementations import (SqlAlchemyCategoryRepository, SqlAlchemyComplaintRepository,
                                              SqlAlchemyNotificationRepository, SqlAlchemyUserRepository)
from app.repositories.interfaces import (CategoryRepository, ComplaintRepository, NotificationRepository,
                                         UserRepository)
from app.services.complaint_service import ComplaintService
from unittest.mock import create_autospec


def test_repositories_implement_interfaces():
    assert issubclass(SqlAlchemyComplaintRepository, ComplaintRepository)
    assert issubclass(SqlAlchemyUserRepository, UserRepository)
    assert issubclass(SqlAlchemyCategoryRepository, CategoryRepository)
    assert issubclass(SqlAlchemyNotificationRepository, NotificationRepository)
    with pytest.raises(TypeError):
        ComplaintRepository()                         # abstract: cannot be instantiated


def test_complaint_repository_crud(app, data):
    repo = SqlAlchemyComplaintRepository()
    c = repo.create(Complaint(complaint_number=repo.next_complaint_number(), student_id=data.student.id,
                              category_id=data.cat.id, title="Repo test", description="Some description", priority="Low"))
    assert repo.get_by_id(c.id).title == "Repo test"
    assert [x.id for x in repo.list_by_student(data.student.id)] == [c.id]
    assert repo.list_by_student(data.student2.id) == []
    c.status, c.assigned_staff_id = "Assigned", data.staff.id
    repo.update(c)
    assert [x.id for x in repo.list_by_staff(data.staff.id)] == [c.id]
    assert repo.search({"status": "Assigned"}) and not repo.search({"status": "Closed"})
    assert repo.search({"q": "repo"}) and not repo.search({"q": "zzz"})


def test_user_and_category_and_notification_repositories(app, data):
    users = SqlAlchemyUserRepository()
    assert users.get_by_email("STU@T.EDU").id == data.student.id
    assert users.count_by_role("staff") == 2
    cats = SqlAlchemyCategoryRepository()
    assert {c.name for c in cats.list_all()} == {"IT", "Facilities"}
    notes = SqlAlchemyNotificationRepository()
    n = notes.create(Notification(user_id=data.student.id, title="t", message="m"))
    assert notes.unread_count(data.student.id) == 1
    notes.mark_read(n)
    assert notes.unread_count(data.student.id) == 0


class InMemoryComplaintRepository(ComplaintRepository):
    """A non-database implementation: proves the service only depends on the interface."""
    def __init__(self):
        self.items = {}

    def create(self, c):
        c.id = len(self.items) + 1
        self.items[c.id] = c
        return c

    def get_by_id(self, i): return self.items.get(i)
    def list_by_student(self, sid): return [c for c in self.items.values() if c.student_id == sid]
    def list_by_staff(self, sid): return [c for c in self.items.values() if c.assigned_staff_id == sid]
    def search(self, filters=None, student_id=None, staff_id=None): return list(self.items.values())
    def update(self, c): self.items[c.id] = c; return c
    def next_complaint_number(self): return f"MOCK-{len(self.items) + 1}"
    def recent(self, limit=5, student_id=None, staff_id=None): return list(self.items.values())[:limit]
    def count_by_status(self, student_id=None, staff_id=None): return {}
    def count_by_priority(self): return {}
    def count_by_category(self): return {}
    def monthly_trend(self, months=6): return []
    def list_overdue(self, days=7): return []
    def staff_performance(self): return []


def test_mock_repository_can_replace_real_repository():
    """Repository Pattern proof: service logic runs with no database or Flask app at all."""
    from app.models import Category, User
    student = User(id=1, full_name="S", email="s@x", role="student", password_hash="x")
    admin = User(id=9, full_name="A", email="a@x", role="admin", password_hash="x")
    staff = User(id=5, full_name="W", email="w@x", role="staff", password_hash="x", is_active=True)

    users = create_autospec(UserRepository, instance=True)
    users.list_by_role.return_value = [admin]
    users.get_by_id.return_value = staff
    categories = create_autospec(CategoryRepository, instance=True)
    categories.get_by_id.return_value = Category(id=1, name="IT")
    notifications = create_autospec(NotificationRepository, instance=True)
    history = create_autospec(__import__("app.repositories.interfaces", fromlist=["x"]).ComplaintHistoryRepository, instance=True)

    repo = InMemoryComplaintRepository()
    svc = ComplaintService(repo, history, notifications, users, categories)

    c = svc.submit(student, 1, "Mock repo title", "Description long enough here", "Low")
    assert c.complaint_number == "MOCK-1" and repo.get_by_id(c.id) is c
    svc.assign(c.id, 5, admin)
    assert repo.get_by_id(c.id).status == "Assigned"
    assert history.create.call_count == 2             # submitted + assigned
    assert notifications.create.called
