from brain.self_development.domain.models import DevelopmentPlan
from brain.self_development.investigation.root_cause_analyzer import (
    RootCauseAnalysis,
)


class ImprovementPlanner:
    """
    Converts investigation results into a structured
    development plan for IRABRAIN.

    Responsibilities:
    - interpret root-cause analysis
    - define an improvement objective
    - create ordered development steps
    - produce a structured plan

    It does NOT:
    - modify source code
    - execute development
    - run tests
    - deploy changes
    - release versions
    """

    def __init__(self):
        self._counter = 0

    def create_plan(
        self,
        analysis: RootCauseAnalysis,
    ) -> DevelopmentPlan:

        if analysis is None:
            raise ValueError(
                "Root-cause analysis cannot be None."
            )

        if not analysis.hypotheses:
            raise ValueError(
                "Root-cause analysis contains no hypotheses."
            )

        primary_hypothesis = max(
            analysis.hypotheses,
            key=lambda item: item.confidence,
        )

        self._counter += 1

        plan_id = f"PLAN-{self._counter:04d}"

        objective = (
            "Improve the system capability associated "
            "with the identified root-cause hypothesis."
        )

        steps = [
            "Define the smallest controlled change required.",
            "Prepare an isolated candidate implementation.",
            "Validate the candidate for correctness and regressions.",
        ]

        constraints = [
            "Do not modify production directly.",
            "Use an isolated development workspace.",
            "Candidate must pass validation before release consideration.",
        ]

        expected_outcome = (
            "The identified issue is addressed without "
            "introducing unacceptable regressions."
        )

        return DevelopmentPlan(
            plan_id=plan_id,
            improvement_id=analysis.improvement_id,
            objective=objective,
            steps=steps,
            constraints=constraints,
            expected_outcome=expected_outcome,
        )