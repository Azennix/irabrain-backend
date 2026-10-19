from brain.memory.repository import MemoryRepository


class SemanticSearch:

    def __init__(
        self,
        repository: MemoryRepository
    ):
        self.repository = repository

    def search_vector(
        self,
        user_id: int,
        query: str
    ):

        return self.repository.search_vector(
            user_id,
            query
        )