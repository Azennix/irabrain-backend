from dataclasses import dataclass, field
from typing import List

from brain.self_development.monitoring.monitoring_policy import (
    MonitoringDecision,
)
from brain.self_development.monitoring.monitoring_response_policy import (
    MonitoringResponse,
)


@dataclass(frozen=True)
class GateDecision:
    """
    Represents the final authorization state of
    a proposed monitoring response.
    """

    allowed: bool
    action: str
    reasons: List[str] = field(
        default_factory=list
    )


class DecisionGate:
    """
    Controls whether a proposed monitoring response
    may proceed to the next layer.

    Responsibilities:
    - evaluate monitoring-policy decision
    - validate proposed response
    - produce an authorization result

    It does NOT:
    - execute rollback
    - deploy changes
    - modify source code
    - release versions
    """

    def evaluate(
        self,
        monitoring_decision: MonitoringDecision,
        response: MonitoringResponse,
    ) -> GateDecision:

        if monitoring_decision is None:
            raise ValueError(
                "Monitoring decision cannot be None."
            )

        if response is None:
            raise ValueError(
                "Monitoring response cannot be None."
            )

        reasons = []

        if not monitoring_decision.actionable:
            reasons.append(
                "Monitoring condition is not actionable."
            )

        if not response.action:
            reasons.append(
                "Monitoring response action is missing."
            )

        return GateDecision(
            allowed=not reasons,
            action=response.action.value,
            reasons=reasons,
        )
