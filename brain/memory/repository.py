from abc import ABC, abstractmethod
from brain.memory.memory_model import Memory


class MemoryRepository(ABC):

    @abstractmethod
    def insert(self, memory: Memory) -> Memory:
        pass

    @abstractmethod
    def update(self, memory: Memory) -> Memory:
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> None:
        pass

    @abstractmethod
    def get_by_id(self, memory_id: str) -> Memory | None:
        pass

    @abstractmethod
    def find_by_key(
        self,
        user_id: int,
        category: str,
        key: str
    ) -> Memory | None:
        pass








    @abstractmethod
    def get_all(
        self,
        user_id: int
    ) -> list[Memory]:
        pass




    @abstractmethod
    def search_keyword(
        self,
        user_id: int,
        query: str
    ):
        pass

    @abstractmethod
    def search_vector(
        self,
        user_id: int,
        query: str
    ):
        pass