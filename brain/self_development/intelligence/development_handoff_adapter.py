from brain.self_development.intelligence.development_execution_request import (
    DevelopmentExecutionRequest,
)
from brain.self_development.intelligence.development_handoff import (
    DevelopmentHandoff,
)


class SelfDevelopmentDevelopmentHandoffAdapter:
    """
    Converts a planning handoff into the execution request
    understood by the Foundation development boundary.

    This adapter does not execute development.
    """

    def build(
        self,
        handoff: DevelopmentHandoff,
    ) -> DevelopmentExecutionRequest:
        if handoff is None:
            raise ValueError(
                "Development handoff cannot be None."
            )

        return DevelopmentExecutionRequest(
            plan_id=handoff.plan_id,
            improvement_id=handoff.improvement_id,
            objective=handoff.objective,
            steps=list(handoff.steps),
            constraints=list(handoff.constraints),
            expected_outcome=handoff.expected_outcome,
            metadata=dict(handoff.metadata),
        )