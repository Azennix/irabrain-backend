from brain.memory.memory_relevance import MemoryRelevance


class MemoryRanker:

    def __init__(self):

        self.relevance = MemoryRelevance()

    def rank(
        self,
        query,
        memories
    ):

        query_embedding = (
            self.relevance.embed_query(
                query
            )
        )

        scored = []

        for memory in memories:

            score = self.relevance.score(
                query_embedding,
                memory
            )

            scored.append(
                (
                    score,
                    memory
                )
            )

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
            memory
            for score, memory in scored
        ]