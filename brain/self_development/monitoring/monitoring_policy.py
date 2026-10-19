from dataclasses import dataclass, field
from typing import List

from brain.self_development.monitoring.alert_manager import (
    Alert,
    AlertSeverity,
)


@dataclass(frozen=True)
class MonitoringDecision:
    """
    Result of monitoring-policy evaluation.
    """

    actionable: bool
    reasons: List[str] = field(
        default_factory=list
    )


class MonitoringPolicy:
    """
    Defines conditions under which monitoring
    observations become actionable.

    It does NOT:
    - perform rollback
    - modify source code
    - deploy changes
    - release versions
    - execute commands
    """

    def __init__(
        self,
        minimum_severity: AlertSeverity = AlertSeverity.HIGH,
    ):
        self.minimum_severity = minimum_severity

    def evaluate(
        self,
        alert: Alert,
    ) -> MonitoringDecision:

        if alert is None:
            raise ValueError(
                "Alert cannot be None."
            )

        severity_order = {
            AlertSeverity.INFO: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.HIGH: 2,
            AlertSeverity.CRITICAL: 3,
        }

        reasons = []

        if (
            severity_order[alert.severity]
            >= severity_order[self.minimum_severity]
        ):
            reasons.append(
                f"Alert severity reached "
                f"the configured threshold: "
                f"{alert.severity.value}"
            )

        return MonitoringDecision(
            actionable=bool(reasons),
            reasons=reasons,
        )