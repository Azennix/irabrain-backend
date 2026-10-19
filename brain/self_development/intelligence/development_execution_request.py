from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DevelopmentExecutionRequest:
    """
    Request handed from the planning boundary to the
    Foundation development stage.

    This identifies the approved plan and the intended
    development context.

    It does not itself authorize or execute development.
    """

    plan_id: str
    improvement_id: str
    objective: str
    steps: list[str]
    constraints: list[str]
    expected_outcome: str
    metadata: dict[str, Any]

    def __post_init__(self):
        if not self.plan_id.strip():
            raise ValueError(
                "Plan ID cannot be empty."
            )

        if not self.improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )

        if not self.objective.strip():
            raise ValueError(
                "Development objective cannot be empty."
            )

        if not self.steps:
            raise ValueError(
                "Development steps cannot be empty."
            )

        if not self.constraints:
            raise ValueError(
                "Development constraints cannot be empty."
            )

        if not self.expected_outcome.strip():
            raise ValueError(
                "Expected outcome cannot be empty."
            )