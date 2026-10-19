class MemoryContextSelector:

    def select_general_context(
        self,
        memories,
        query=None,
        max_memories=5
    ):

        scored = []

        for memory in memories:

            importance_score = (
                memory.importance
            )

            confidence_score = (
                memory.confidence
            )

            access_score = min(
                memory.access_count,
                10
            ) / 10.0

            score = (
                importance_score * 0.50
                + confidence_score * 0.30
                + access_score * 0.20
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
            for score, memory in scored[:max_memories]
        ]