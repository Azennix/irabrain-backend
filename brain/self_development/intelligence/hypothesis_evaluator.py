from dataclasses import dataclass

from brain.self_development.intelligence.improvement_hypothesis import (
    ImprovementHypothesis,
)


@dataclass(frozen=True)
class HypothesisEvaluation:
    """
    Evaluation of an Intelligence-generated hypothesis.

    This is a decision about evidence quality only.
    It does not authorize or execute any action.
    """

    hypothesis_id: str
    supported: bool
    confidence: float
    reason: str


class SelfDevelopmentHypothesisEvaluator:
    """
    Evaluates whether a hypothesis has enough confidence
    to become a candidate for further planning.
    """

    MIN_CONFIDENCE = 0.5

    def evaluate(
        self,
        hypothesis: ImprovementHypothesis,
    ) -> HypothesisEvaluation:
        if hypothesis is None:
            raise ValueError(
                "Improvement hypothesis cannot be None."
            )

        supported = (
            hypothesis.confidence
            >= self.MIN_CONFIDENCE
        )

        if supported:
            reason = (
                "Hypothesis has sufficient confidence "
                "for further consideration."
            )
        else:
            reason = (
                "Hypothesis confidence is below the "
                "minimum threshold."
            )

        return HypothesisEvaluation(
            hypothesis_id=hypothesis.hypothesis_id,
            supported=supported,
            confidence=hypothesis.confidence,
            reason=reason,
        )