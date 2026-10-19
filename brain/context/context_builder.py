
from brain.memory.access_tracker import MemoryAccessTracker
from brain.retrieval.memory_budget import MemoryBudget
from brain.context.final_context_selector import FinalContextSelector
from brain.memory.recency_scorer import RecencyScorer
from brain.retrieval.memory_score import MemoryScore
from brain.context.context_relevance_gate import ContextRelevanceGate
from brain.context.context_compressor import ContextCompressor
from brain.memory.repository import MemoryRepository
class ContextBuilder:

    """
    Builds the final memory context used by IRABrain.

    Responsibilities:

    1. Process relevant memories
    2. Apply memory budget
    3. Track memory access
    4. Calculate memory scores
    5. Select final memories
    6. Apply context relevance filtering
    7. Compress the selected memories

    It does NOT:

    - extract memories
    - write memories
    - resolve memories
    - generate responses
    - perform reasoning
    """

    def __init__(
        self,
        repository: MemoryRepository

    ):
        self.repository = repository

        self.access_tracker = MemoryAccessTracker(
            self.repository
        )

        self.memory_budget = MemoryBudget()

        self.final_selector = FinalContextSelector()

        self.recency_scorer = RecencyScorer()

        self.memory_score = MemoryScore()

        self.context_relevance_gate = (
            ContextRelevanceGate()
        )

        self.context_compressor = ContextCompressor()

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    def build(
        self,
        user_id: int,
        user_message: str,
        memories=None,
        include_memory: bool = True
    ):
        """
        Build the final memory context.

        include_memory=False:
            Skip memory retrieval completely.

        include_memory=True:
            Run the complete memory-context pipeline.
        """

        # =================================================
        # MEMORY DISABLED
        # =================================================

        if not include_memory or not memories:

            print(
                "\n===== MEMORY CONTEXT DISABLED =====\n"
            )

            return self.context_compressor.compress(
                []
            )





# continue with MEMORY BUDGET

        # =================================================
        # DEBUG — BEFORE BUDGET
        # =================================================

        print(
            "\n===== BEFORE MEMORY BUDGET ====="
        )

        for memory in memories:

            print(
                memory.category,
                memory.key,
                memory.value
            )

        print(
            "================================\n"
        )

        # =================================================
        # 1. MEMORY BUDGET
        # =================================================

        memories = self.memory_budget.apply(
            memories
        )

        # =================================================
        # NO MEMORIES AFTER BUDGET
        # =================================================

        if not memories:

            print(
                "\n===== NO MEMORIES AFTER BUDGET =====\n"
            )

            return self.context_compressor.compress(
                []
            )

        # =================================================
        # DEBUG — AFTER BUDGET
        # =================================================

        print(
            "\n===== AFTER MEMORY BUDGET ====="
        )

        for memory in memories:

            print(
                memory.category,
                memory.key,
                memory.value
            )

        print(
            "================================\n"
        )

        # =================================================
        # 3. ACCESS TRACKING
        # =================================================

        memories = self.access_tracker.track(
            memories
        )

        # =================================================
        # NO MEMORIES AFTER ACCESS TRACKING
        # =================================================

        if not memories:

            print(
                "\n===== NO MEMORIES AFTER ACCESS TRACKING =====\n"
            )

            return self.context_compressor.compress(
                []
            )

        # =================================================
        # 4. MEMORY SCORING
        # =================================================

        print(
            "\n===== MEMORY SCORES ====="
        )

        memory_scores = {}

        for memory in memories:

            recency = self.recency_scorer.score(
                memory.last_accessed
            )

            score = self.memory_score.score(
                importance=memory.importance,
                confidence=memory.confidence,
                access=memory.access_count,
                recency=recency
            )

            memory_scores[
                memory.memory_id
            ] = score

            print(
                f"{memory.key} | "
                f"retrieval={memory.retrieval_score:.3f} | "
                f"importance={memory.importance:.3f} | "
                f"confidence={memory.confidence:.3f} | "
                f"access={memory.access_count} | "
                f"recency={recency:.3f} | "
                f"memory_score={score:.3f}"
            )

        print(
            "=========================\n"
        )

        # =================================================
        # 5. RECENCY DEBUG
        # =================================================

        print(
            "\n===== RECENCY SCORES ====="
        )

        for memory in memories:

            recency = self.recency_scorer.score(
                memory.last_accessed
            )

            print(
                f"{memory.key} | "
                f"last_accessed={memory.last_accessed} | "
                f"recency={recency:.3f}"
            )

        print(
            "==========================\n"
        )

        # =================================================
        # 6. FINAL MEMORY SELECTION
        # =================================================

        selected_scores = (
            self.final_selector.select(
                memories,
                memory_scores
            )
        )

        # =================================================
        # 7. CONTEXT RELEVANCE GATE
        # =================================================

        selected_scores = (
            self.context_relevance_gate.filter(
                scores=selected_scores
            )
        )

        # =================================================
        # NO MEMORIES AFTER RELEVANCE GATE
        # =================================================

        if not selected_scores:

            print(
                "\n===== NO MEMORIES PASSED RELEVANCE GATE =====\n"
            )

            return self.context_compressor.compress(
                []
            )

        # =================================================
        # DEBUG — FINAL SCORES
        # =================================================

        print(
            "\n===== AFTER CONTEXT RELEVANCE GATE ====="
        )

        for score in selected_scores:

            memory = score.memory

            print(
                f"{memory.key} | "
                f"retrieval={score.retrieval_score:.3f} | "
                f"memory_score={score.memory_score:.3f} | "
                f"context_score={score.context_score:.3f} | "
                f"importance={memory.importance:.3f} | "
                f"confidence={memory.confidence:.3f} | "
                f"access={memory.access_count}"
            )

        print(
            "=========================================\n"
        )

        # =================================================
        # 8. CONTEXT COMPRESSION
        # =================================================

        print(
            "\n===== CONTEXT COMPRESSION ====="
        )

        context = self.context_compressor.compress(
            selected_scores
        )

        print(
            context
        )

        print(
            "===============================\n"
        )

        # =================================================
        # FINAL CONTEXT
        # =================================================

        print(
            "\n===== FINAL CONTEXT ====="
        )

        print(
            context
        )

        print(
            "=========================\n"
        )

        return context