from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from brain.self_development.monitoring.decision_gate import (
    GateDecision,
)


@dataclass(frozen=True)
class ResponseExecutionResult:
    """
    Result of a controlled monitoring response execution.
    """

    success: bool
    action: str
    message: str
    executed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class ResponseExecutor:
    """
    Executes only explicitly supported monitoring responses.

    Responsibilities:
    - verify an authorized gate decision
    - execute the supported response category
    - return a structured execution result

    It does NOT:
    - modify source code
    - deploy versions
    - perform unrestricted rollback
    - release production
    - execute arbitrary commands
    """

    ALLOWED_ACTIONS = {
        "observe",
        "investigate",
        "rollback",
        "escalate",
    }

    def execute(
        self,
        decision: GateDecision,
    ) -> ResponseExecutionResult:

        if decision is None:
            raise ValueError(
                "Gate decision cannot be None."
            )

        if not decision.allowed:
            return ResponseExecutionResult(
                success=False,
                action=decision.action,
                message=(
                    "Response execution blocked: "
                    "decision was not authorized."
                ),
            )

        if decision.action not in self.ALLOWED_ACTIONS:
            raise ValueError(
                f"Unsupported response action: "
                f"{decision.action}"
            )

        return ResponseExecutionResult(
            success=True,
            action=decision.action,
            message=(
                f"Authorized response registered: "
                f"{decision.action}"
            ),
        )