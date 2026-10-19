from database.conversation import MemoryEntity
from brain.memory.repository import MemoryRepository


class KeywordSearch:

    def __init__(
        self,
        repository: MemoryRepository
    ):
        self.repository = repository

    def search_keyword(
        self,
        user_id: int,
        query: str
    ):
        entities =(
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.user_id == user_id,
                MemoryEntity.key.ilike(f"%{query}%")
            )
            .all()
        )

        return [
            self._to_domain(entity)
            for entity in entities
        ]