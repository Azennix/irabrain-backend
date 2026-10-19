from brain.memory.repository import MemoryRepository


class MemoryRetriever:

    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def retrieve(
        self,
        user_id: int,
        query: str
    ):

        keyword_results = self.repository.search_keyword(
            user_id,
            query
        )

        vector_results = self.repository.search_vector(
            user_id,
            query
        )

        merged = {}

        for memory in keyword_results:
            merged[memory.memory_id] = memory

        for memory in vector_results:
            merged[memory.memory_id] = memory

        return list(merged.values())