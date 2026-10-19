from brain.retrieval.retrieval_result import RetrievalResult


class DuplicateFilter:

    def filter(
        self,
        results: list[RetrievalResult]
    ) -> list[RetrievalResult]:

        unique = {}

        for result in results:

            key = (
                result.memory.user_id,
                result.memory.category,
                result.memory.key
            )

            if key not in unique:

                unique[key] = result

                continue

            existing = unique[key]

            # --------------------------------
            # MERGE RETRIEVAL EVIDENCE
            # --------------------------------

            existing.keyword_score = max(
                existing.keyword_score,
                result.keyword_score
            )

            existing.semantic_score = max(
                existing.semantic_score,
                result.semantic_score
            )

            existing.association_score = max(
                existing.association_score,
                result.association_score
            )

            existing.concept_score = max(
                existing.concept_score,
                result.concept_score
            )

        return list(unique.values())