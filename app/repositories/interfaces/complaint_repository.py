from abc import ABC, abstractmethod


class ComplaintRepository(ABC):
    """Contract for complaint persistence. Services depend on this, never on SQLAlchemy."""

    @abstractmethod
    def create(self, complaint): ...

    @abstractmethod
    def get_by_id(self, complaint_id): ...

    @abstractmethod
    def list_by_student(self, student_id): ...

    @abstractmethod
    def list_by_staff(self, staff_id): ...

    @abstractmethod
    def search(self, filters=None, student_id=None, staff_id=None): ...

    @abstractmethod
    def update(self, complaint): ...

    @abstractmethod
    def next_complaint_number(self): ...

    @abstractmethod
    def recent(self, limit=5, student_id=None, staff_id=None): ...

    @abstractmethod
    def count_by_status(self, student_id=None, staff_id=None): ...

    @abstractmethod
    def count_by_priority(self): ...

    @abstractmethod
    def count_by_category(self): ...

    @abstractmethod
    def monthly_trend(self, months=6): ...

    @abstractmethod
    def list_overdue(self, days=7): ...

    @abstractmethod
    def staff_performance(self): ...
