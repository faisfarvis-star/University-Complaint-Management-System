from abc import ABC, abstractmethod


class CategoryRepository(ABC):
    @abstractmethod
    def create(self, category): ...

    @abstractmethod
    def get_by_id(self, category_id): ...

    @abstractmethod
    def get_by_name(self, name): ...

    @abstractmethod
    def list_all(self): ...

    @abstractmethod
    def update(self, category): ...

    @abstractmethod
    def delete(self, category): ...

    @abstractmethod
    def complaint_count(self, category_id): ...
