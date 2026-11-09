from abc import ABC, abstractmethod


class ComplaintHistoryRepository(ABC):
    @abstractmethod
    def create(self, entry): ...

    @abstractmethod
    def list_by_complaint(self, complaint_id): ...
