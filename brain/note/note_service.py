from datetime import datetime
import uuid

from .note_model import Note
from .note_repository import NoteRepository


class NoteService:

    def __init__(self, repository: NoteRepository):
        self.repository = repository

    def create_note(
        self,
        user_id: int,
        title: str,
        content: str,
    ) -> Note:

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Note title is required.")

        now = datetime.utcnow()

        note = Note(
            note_id=str(uuid.uuid4()),
            user_id=user_id,
            title=normalized_title,
            content=content,
            created_at=now,
            updated_at=now,
        )

        return self.repository.create(note)

    def get_note(
        self,
        user_id: int,
        note_id: str,
    ) -> Note | None:

        return self.repository.get_by_id(
            note_id=note_id,
            user_id=user_id,
        )

    def get_notes(
        self,
        user_id: int,
    ) -> list[Note]:

        return self.repository.get_all(
            user_id=user_id,
        )

    def update_note(
        self,
        user_id: int,
        note_id: str,
        title: str,
        content: str,
    ) -> Note:

        note = self.repository.get_by_id(
            note_id=note_id,
            user_id=user_id,
        )

        if note is None:
            raise ValueError("Note not found.")

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Note title is required.")

        note.title = normalized_title
        note.content = content
        note.updated_at = datetime.utcnow()

        return self.repository.update(note)

    def delete_note(
        self,
        user_id: int,
        note_id: str,
    ) -> bool:

        return self.repository.delete(
            note_id=note_id,
            user_id=user_id,
        )