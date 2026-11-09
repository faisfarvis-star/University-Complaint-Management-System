from abc import ABC, abstractmethod


class NotificationRepository(ABC):
    @abstractmethod
    def create(self, notification): ...

    @abstractmethod
    def get_by_id(self, notification_id): ...

    @abstractmethod
    def list_for_user(self, user_id, limit=100): ...

    @abstractmethod
    def unread_count(self, user_id): ...

    @abstractmethod
    def mark_read(self, notification): ...

    @abstractmethod
    def mark_all_read(self, user_id): ...
