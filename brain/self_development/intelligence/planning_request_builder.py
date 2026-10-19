from brain.self_development.intelligence.improvement_candidate import (
    ImprovementCandidate,
)
from brain.self_development.intelligence.planning_request import (
    ImprovementPlanningRequest,
)


class SelfDevelopmentPlanningRequestBuilder:
    """
    Converts a validated ImprovementCandidate into a
    planning request for the Foundation.

    This is a handoff only.

    It does not:
    - create the development plan
    - execute development
    - authorize changes
    - deploy or release anything
    """

    def build(
        self,
        candidate: ImprovementCandidate,
    ) -> ImprovementPlanningRequest:
        if candidate is None:
            raise ValueError(
                "Improvement candidate cannot be None."
            )

        return ImprovementPlanningRequest(
            candidate_id=candidate.candidate_id,
            hypothesis_id=candidate.hypothesis_id,
            statement=candidate.statement,
            confidence=candidate.confidence,
            evidence=dict(candidate.evidence),
        )