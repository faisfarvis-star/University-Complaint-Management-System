from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    def create(self, user): ...

    @abstractmethod
    def get_by_id(self, user_id): ...

    @abstractmethod
    def get_by_email(self, email): ...

    @abstractmethod
    def get_by_registration_number(self, registration_number): ...

    @abstractmethod
    def list_by_role(self, role, active_only=False): ...

    @abstractmethod
    def update(self, user): ...

    @abstractmethod
    def count_by_role(self, role): ...
