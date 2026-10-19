from fastapi import Depends
from sqlalchemy.orm import Session

from database.dependencies import get_db
from brain.note.note_service import NoteService
from brain.note.sqlalchemy_note_repository import SQLAlchemyNoteRepository


def get_note_service(
    db: Session = Depends(get_db),
) -> NoteService:
    repository = SQLAlchemyNoteRepository(session=db)
    return NoteService(repository=repository)