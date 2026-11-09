from abc import ABC, abstractmethod


class CommentRepository(ABC):
    @abstractmethod
    def create(self, comment): ...

    @abstractmethod
    def list_by_complaint(self, complaint_id): ...


class AttachmentRepository(ABC):
    @abstractmethod
    def create(self, attachment): ...

    @abstractmethod
    def get_by_id(self, attachment_id): ...

    @abstractmethod
    def list_by_complaint(self, complaint_id): ...


class AuditLogRepository(ABC):
    @abstractmethod
    def create(self, entry): ...

    @abstractmethod
    def list_recent(self, limit=200): ...
