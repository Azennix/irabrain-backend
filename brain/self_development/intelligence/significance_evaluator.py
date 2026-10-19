from dataclasses import dataclass

from brain.self_development.intelligence.observer import (
    SelfDevelopmentObservation,
)


@dataclass(frozen=True)
class SignificanceDecision:
    """
    Determines whether a self-development observation
    should proceed to investigation.

    This is a decision about investigation only.
    It does not authorize or execute any change.
    """

    requires_investigation: bool
    reason: str


class SelfDevelopmentSignificanceEvaluator:

    def evaluate(
        self,
        observation: SelfDevelopmentObservation,
    ) -> SignificanceDecision:

        if observation is None:
            raise ValueError(
                "Self-development observation cannot be None."
            )

        if observation.requires_investigation:

            return SignificanceDecision(
                requires_investigation=True,
                reason="Observation requires investigation.",
            )

        return SignificanceDecision(
            requires_investigation=False,
            reason="Observation does not require investigation.",
        )