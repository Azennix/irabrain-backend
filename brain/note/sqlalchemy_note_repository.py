from sqlalchemy.orm import Session

from database.models import NoteEntity

from .note_model import Note
from .note_repository import NoteRepository


class SQLAlchemyNoteRepository(NoteRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, note: Note) -> Note:
        entity = NoteEntity(
            note_id=note.note_id,
            user_id=note.user_id,
            title=note.title,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )

        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)

        return self._to_domain(entity)

    def get_by_id(
        self,
        note_id: str,
        user_id: int,
    ) -> Note | None:

        entity = (
            self.session.query(NoteEntity)
            .filter(
                NoteEntity.note_id == note_id,
                NoteEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return None

        return self._to_domain(entity)

    def get_all(
        self,
        user_id: int,
    ) -> list[Note]:

        entities = (
            self.session.query(NoteEntity)
            .filter(
                NoteEntity.user_id == user_id,
            )
            .order_by(NoteEntity.updated_at.desc())
            .all()
        )

        return [
            self._to_domain(entity)
            for entity in entities
        ]

    def update(self, note: Note) -> Note:

        entity = (
            self.session.query(NoteEntity)
            .filter(
                NoteEntity.note_id == note.note_id,
                NoteEntity.user_id == note.user_id,
            )
            .first()
        )

        if entity is None:
            raise ValueError("Note not found.")

        entity.title = note.title
        entity.content = note.content
        entity.updated_at = note.updated_at

        self.session.commit()
        self.session.refresh(entity)

        return self._to_domain(entity)

    def delete(
        self,
        note_id: str,
        user_id: int,
    ) -> bool:

        entity = (
            self.session.query(NoteEntity)
            .filter(
                NoteEntity.note_id == note_id,
                NoteEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return False

        self.session.delete(entity)
        self.session.commit()

        return True

    @staticmethod
    def _to_domain(entity: NoteEntity) -> Note:
        return Note(
            note_id=entity.note_id,
            user_id=entity.user_id,
            title=entity.title,
            content=entity.content,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )