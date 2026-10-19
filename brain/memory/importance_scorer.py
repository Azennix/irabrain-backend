from brain.memory.memory_model import Memory


class MemoryImportanceScorer:

    DEFAULT_SCORE = 0.50

    def score(
        self,
        memory: Memory
    ) -> float:

        score = self.DEFAULT_SCORE

        # Confidence
        score += (memory.confidence - 0.5) * 0.20

        # Existing importance can be used as a signal
        score += (memory.importance - 0.5) * 0.20

        return max(0.0, min(1.0, score))