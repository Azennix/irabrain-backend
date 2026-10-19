from brain.self_development.intelligence.observer import (
    SelfDevelopmentObservation,
)
from brain.self_development.intelligence.significance_evaluator import (
    SignificanceDecision,
)
from brain.self_development.intelligence.investigation_request import (
    InvestigationRequest,
)


class SelfDevelopmentInvestigator:

    def create_request(
        self,
        observation: SelfDevelopmentObservation,
        decision: SignificanceDecision,
    ) -> InvestigationRequest | None:

        if observation is None:
            raise ValueError(
                "Self-development observation cannot be None."
            )

        if decision is None:
            raise ValueError(
                "Significance decision cannot be None."
            )

        if not decision.requires_investigation:
            return None

        return InvestigationRequest(
            observation_id=observation.signal_id,
            operation=observation.operation,
            reason=decision.reason,
            evidence=dict(observation.evidence),
        )