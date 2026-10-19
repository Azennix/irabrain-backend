from fastapi import APIRouter, Depends, HTTPException

from security.dependencies import get_current_user

from api.note_dependencies import get_note_service
from brain.note.note_service import NoteService


router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
)


@router.post("")
def create_note(
    title: str,
    content: str,
    current_user=Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
):
    try:
        note = note_service.create_note(
            user_id=current_user.user_id,
            title=title,
            content=content,
        )

        return {
            "note": {
                "note_id": note.note_id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            }
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("")
def get_notes(
    current_user=Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
):
    notes = note_service.get_notes(
        user_id=current_user.user_id,
    )

    return {
        "notes": [
            {
                "note_id": note.note_id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            }
            for note in notes
        ]
    }


@router.get("/{note_id}")
def get_note(
    note_id: str,
    current_user=Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
):
    note = note_service.get_note(
        user_id=current_user.user_id,
        note_id=note_id,
    )

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found.",
        )

    return {
        "note": {
            "note_id": note.note_id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
        }
    }


@router.patch("/{note_id}")
def update_note(
    note_id: str,
    title: str,
    content: str,
    current_user=Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
):
    try:
        note = note_service.update_note(
            user_id=current_user.user_id,
            note_id=note_id,
            title=title,
            content=content,
        )

        return {
            "note": {
                "note_id": note.note_id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            }
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.delete("/{note_id}")
def delete_note(
    note_id: str,
    current_user=Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
):
    deleted = note_service.delete_note(
        user_id=current_user.user_id,
        note_id=note_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Note not found.",
        )

    return {
        "success": True,
    }