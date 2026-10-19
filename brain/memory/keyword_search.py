from database.conversation import MemoryEntity


class KeywordSearch:

    def __init__(self, session):
        self.session = session

    def search(
        self,
        user_id: int,
        query: str
    ):

        return (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.user_id == user_id,
                (
                    MemoryEntity.key.ilike(f"%{query}%")
                    |
                    MemoryEntity.value.ilike(f"%{query}%")
                )
            )
            .all()
        )