from dataclasses import dataclass, field
from enum import Enum
from typing import List

from brain.self_development.monitoring.alert_manager import (
    Alert,
    AlertSeverity,
)


class ResponseAction(str, Enum):
    OBSERVE = "observe"
    INVESTIGATE = "investigate"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class MonitoringResponse:
    """
    Represents a proposed response to a monitoring alert.
    """

    alert_id: str
    action: ResponseAction
    reasons: List[str] = field(
        default_factory=list
    )


class MonitoringResponsePolicy:
    """
    Determines the appropriate response category
    for an actionable monitoring alert.

    It does NOT:
    - execute rollback
    - deploy changes
    - modify source code
    - release versions
    """

    def determine(
        self,
        alert: Alert,
    ) -> MonitoringResponse:

        if alert is None:
            raise ValueError(
                "Alert cannot be None."
            )

        if alert.severity == AlertSeverity.CRITICAL:
            action = ResponseAction.ROLLBACK
            reason = (
                "Critical alert requires rollback evaluation."
            )

        elif alert.severity == AlertSeverity.HIGH:
            action = ResponseAction.INVESTIGATE
            reason = (
                "High-severity alert requires investigation."
            )

        elif alert.severity == AlertSeverity.WARNING:
            action = ResponseAction.OBSERVE
            reason = (
                "Warning alert should remain under observation."
            )

        else:
            action = ResponseAction.OBSERVE
            reason = (
                "Informational alert requires observation."
            )

        return MonitoringResponse(
            alert_id=alert.alert_id,
            action=action,
            reasons=[reason],
        )