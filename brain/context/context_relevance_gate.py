from brain.context.context_config import ContextConfig
from brain.context.context_score import ContextScore


class ContextRelevanceGate:

    def __init__(
        self,
        config: ContextConfig | None = None
    ):
        self.config = config or ContextConfig()

    def filter(
        self,
        scores: list[ContextScore]
    ) -> list[ContextScore]:

        if not scores:
            return []

        print("\n===== RELEVANCE GATE =====")

        accepted = []

        for score in scores:

            passed = (
                score.context_score
                >= self.config.min_context_score
            )

            print(
                f"{score.memory.key} | "
                f"context={score.context_score:.3f} | "
                f"threshold={self.config.min_context_score:.3f} | "
                f"{'KEEP' if passed else 'DROP'}"
            )

            if passed:
                accepted.append(score)

        print("==========================\n")

        return accepted