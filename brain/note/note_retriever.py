from brain.note.note_model import Note


class NoteRetriever:

    def __init__(self, repository):
        self.repository = repository

    def retrieve(
        self,
        user_id: int,
        query: str,
        limit: int = 5
    ) -> list[Note]:

        notes = self.repository.get_all(user_id=user_id)

        if not notes:
            return []

        query_words = {
            word.lower()
            for word in query.split()
            if len(word.strip()) >= 3
        }

        if not query_words:
            return []

        scored_notes = []

        for note in notes:

            searchable_text = (
                f"{note.title} {note.content}"
            ).lower()

            score = sum(
                1
                for word in query_words
                if word in searchable_text
            )

            if score > 0:
                scored_notes.append(
                    (score, note)
                )

        scored_notes.sort(
            key=lambda item: (
                -item[0],
                item[1].updated_at
            )
        )

        return [
            note
            for _, note in scored_notes[:limit]
        ]