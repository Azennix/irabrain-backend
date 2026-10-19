from abc import ABC, abstractmethod

from .note_model import Note


class NoteRepository(ABC):

    @abstractmethod
    def create(self, note: Note) -> Note:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        note_id: str,
        user_id: int,
    ) -> Note | None:
        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
        user_id: int,
    ) -> list[Note]:
        raise NotImplementedError

    @abstractmethod
    def update(self, note: Note) -> Note:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        note_id: str,
        user_id: int,
    ) -> bool:
        raise NotImplementedError