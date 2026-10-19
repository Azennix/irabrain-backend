import numpy as np

from brain.embeddings.embedding_service import EmbeddingService


class MemoryRelevance:

    def __init__(self):

        self.embedding_service = EmbeddingService()

    def embed_query(
        self,
        query: str
    ) -> list[float]:

        return self.embedding_service.generate(
            query
        )

    def score(
        self,
        query_embedding: list[float],
        memory
    ) -> float:

        memory_embedding = memory.embedding

        if not memory_embedding:
            return 0.0

        query_vector = np.array(
            query_embedding,
            dtype=float
        )

        memory_vector = np.array(
            memory_embedding,
            dtype=float
        )

        query_norm = np.linalg.norm(
            query_vector
        )

        memory_norm = np.linalg.norm(
            memory_vector
        )

        if query_norm == 0 or memory_norm == 0:
            return 0.0

        similarity = float(
            np.dot(
                query_vector,
                memory_vector
            )
            /
            (
                query_norm
                * memory_norm
            )
        )

        return max(
            0.0,
            min(
                similarity,
                1.0
            )
        )