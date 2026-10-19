from brain.context.context_config import ContextConfig
from brain.context.context_score import ContextScore


class FinalContextSelector:

    def __init__(
        self,
        config: ContextConfig | None = None
    ):
        self.config = config or ContextConfig()

    def select(
        self,
        memories,
        memory_scores
    ):

        if not memories:
            return []

        # ================================================
        # CONTEXT SCORES
        # ================================================

        print("\n===== CONTEXT SCORES =====")

        for memory in memories:

            memory_score = memory_scores.get(
                memory.memory_id,
                0.0
            )

            print(
                memory.key,
                "| retrieval=",
                round(memory.retrieval_score, 3),
                "| memory_score=",
                round(memory_score, 3),
                "| importance=",
                round(memory.importance, 3),
                "| confidence=",
                round(memory.confidence, 3),
                "| access=",
                memory.access_count
            )

            print("==========================")

        # ================================================
        # MIN RETRIEVAL FILTER
        # ================================================

        memories = [
            memory
            for memory in memories
            if memory.retrieval_score
            >= self.config.min_retrieval_score
        ]

        # ================================================
        # CALCULATE CONTEXT SCORE
        # ================================================

        scored_memories = []

        for memory in memories:

            memory_score = memory_scores.get(
                memory.memory_id,
                0.0
            )

            context_score = (
                memory.retrieval_score
                * self.config.retrieval_weight
                + memory_score
                * self.config.memory_weight
            )

            scored_memories.append(
                ContextScore(
                    memory=memory,
                    retrieval_score=memory.retrieval_score,
                    memory_score=memory_score,
                    context_score=context_score
                )
            )

        # ================================================
        # BEST CONTEXT FIRST
        # ================================================

        scored_memories.sort(
            key=lambda item: item.context_score,
            reverse=True
        )

        # ================================================
        # FINAL MEMORY LIMIT
        # ================================================

        return scored_memories[
            :self.config.max_memories
        ]