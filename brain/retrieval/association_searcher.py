from brain.embeddings.embedding_service import EmbeddingService
from brain.embeddings.similarity import SimilarityService


class AssociationSearcher:

    def __init__(
        self,
        threshold: float = 0.25
    ):

        self.embedding_service = EmbeddingService()
        self.similarity_service = SimilarityService()

        self.threshold = threshold

    def search(
        self,
        query: str,
        memory_associations
    ):

        if not query.strip():
            return []

        # --------------------------------
        # QUERY EMBEDDING
        # --------------------------------

        query_embedding = (
            self.embedding_service.generate(
                query
            )
        )

        matches = []

        # --------------------------------
        # SEMANTIC SEARCH
        # --------------------------------

        for memory_id, association in memory_associations.items():

            if not association:
                continue

            association_embedding = (
                association.get("embedding")
            )

            if association_embedding is None:
                continue

            similarity = (
                self.similarity_service.cosine_similarity(
                    query_embedding,
                    association_embedding
                )
            )

            print(
                "ASSOCIATION:",
                memory_id,
                "->",
                round(similarity, 3)
            )

            # --------------------------------
            # THRESHOLD
            # --------------------------------

            if similarity >= self.threshold:

                matches.append(
                    (
                        memory_id,
                        similarity
                    )
                )

        # --------------------------------
        # BEST FIRST
        # --------------------------------

        matches.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return matches