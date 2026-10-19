from brain.self_development.domain.models import Evidence
from brain.self_development.investigation.root_cause_analyzer import (
    RootCauseAnalysis,
    RootCauseHypothesis,
)
from brain.self_development.intelligence.planning_request import (
    ImprovementPlanningRequest,
)


class SelfDevelopmentPlanningAdapter:
    """
    Converts an Intelligence planning request into the
    RootCauseAnalysis contract expected by the existing
    Foundation ImprovementPlanner.

    This adapter does not create or execute a development plan.
    """

    def create_analysis(
        self,
        request: ImprovementPlanningRequest,
    ) -> RootCauseAnalysis:
        if request is None:
            raise ValueError(
                "Planning request cannot be None."
            )

        evidence_items = []

        for index, (source, data) in enumerate(
            request.evidence.items(),
            start=1,
        ):
            evidence_items.append(
                Evidence(
                    evidence_id=f"INT-EVD-{index:04d}",
                    source="intelligence",
                    description=f"Intelligence evidence: {source}",
                    data={
                        "source": source,
                        "value": data,
                    },
                )
            )

        hypothesis = RootCauseHypothesis(
            statement=request.statement,
            confidence=request.confidence,
            supporting_evidence=evidence_items,
        )

        return RootCauseAnalysis(
            improvement_id=request.candidate_id,
            hypotheses=[hypothesis],
        )