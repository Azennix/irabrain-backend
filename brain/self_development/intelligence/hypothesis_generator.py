from brain.self_development.intelligence.investigation_outcome import (
    InvestigationOutcome,
)
from brain.self_development.intelligence.improvement_hypothesis import (
    ImprovementHypothesis,
)


class SelfDevelopmentHypothesisGenerator:
    """
    Generates candidate improvement hypotheses from
    investigation outcomes.

    This layer proposes possibilities only.

    It does not:
    - execute development
    - modify code
    - authorize changes
    - release or deploy anything
    """

    def generate(
        self,
        outcome: InvestigationOutcome,
    ) -> ImprovementHypothesis | None:
        if outcome is None:
            raise ValueError(
                "Investigation outcome cannot be None."
            )

        if outcome.status != "completed":
            return None

        if not outcome.actionable:
            return None

        hypotheses = outcome.evidence.get(
            "hypotheses",
            [],
        )

        if not hypotheses:
            return None

        first_hypothesis = hypotheses[0]

        if isinstance(first_hypothesis, dict):
            statement = first_hypothesis.get(
                "statement",
                "",
            )
            confidence = first_hypothesis.get(
                "confidence",
                0.0,
            )
        else:
            statement = str(first_hypothesis)
            confidence = 0.0

        if not statement.strip():
            return None

        return ImprovementHypothesis(
            hypothesis_id=(
                f"HYP-{outcome.evidence.get('improvement_id', 'UNKNOWN')}"
            ),
            statement=statement,
            confidence=float(confidence),
            evidence=dict(outcome.evidence),
        )