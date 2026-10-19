from dataclasses import dataclass
from typing import Any

from brain.self_development.domain.models import DevelopmentPlan


@dataclass(frozen=True)
class DevelopmentHandoff:
    """
    Explicit handoff from the planning boundary to the
    existing Self-Development Foundation.

    This carries a plan only.

    It does not:
    - authorize development
    - execute development
    - modify files
    - deploy changes
    - release versions
    """

    plan_id: str
    improvement_id: str
    objective: str
    steps: list[str]
    constraints: list[str]
    expected_outcome: str
    metadata: dict[str, Any]

    @classmethod
    def from_plan(
        cls,
        plan: DevelopmentPlan,
    ) -> "DevelopmentHandoff":
        if plan is None:
            raise ValueError(
                "Development plan cannot be None."
            )

        return cls(
            plan_id=plan.plan_id,
            improvement_id=plan.improvement_id,
            objective=plan.objective,
            steps=list(plan.steps),
            constraints=list(plan.constraints),
            expected_outcome=plan.expected_outcome,
            metadata={},
        )