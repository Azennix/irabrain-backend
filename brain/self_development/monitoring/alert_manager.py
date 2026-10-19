from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class Alert:
    """
    Represents a monitoring alert generated
    from an observed system condition.
    """

    alert_id: str
    target_id: str
    severity: AlertSeverity
    message: str
    status: AlertStatus = AlertStatus.OPEN
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )
    resolved_at: Optional[datetime] = None


class AlertManager:
    """
    Manages structured monitoring alerts.

    Responsibilities:
    - create alerts
    - assign alert severity
    - track alert status
    - acknowledge alerts
    - resolve alerts
    - retrieve alerts

    It does NOT:
    - perform rollback
    - modify source code
    - deploy changes
    - release versions
    - make final release decisions
    """

    def __init__(self):
        self._alerts: Dict[str, Alert] = {}
        self._counter = 0

    def create(
        self,
        target_id: str,
        severity: AlertSeverity,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> Alert:

        if not target_id.strip():
            raise ValueError(
                "Target ID cannot be empty."
            )

        if not isinstance(
            severity,
            AlertSeverity,
        ):
            raise ValueError(
                "Invalid alert severity."
            )

        if not message.strip():
            raise ValueError(
                "Alert message cannot be empty."
            )

        self._counter += 1

        alert_id = (
            f"ALT-{self._counter:04d}"
        )

        alert = Alert(
            alert_id=alert_id,
            target_id=target_id,
            severity=severity,
            message=message,
            metadata=(
                dict(metadata)
                if metadata is not None
                else {}
            ),
        )

        self._alerts[alert_id] = alert

        return alert

    def get(
        self,
        alert_id: str,
    ) -> Optional[Alert]:

        return self._alerts.get(
            alert_id
        )

    def acknowledge(
        self,
        alert_id: str,
    ) -> Alert:

        alert = self._get(alert_id)

        if alert.status != AlertStatus.OPEN:
            raise ValueError(
                "Only an open alert can be acknowledged."
            )

        alert.status = AlertStatus.ACKNOWLEDGED

        return alert

    def resolve(
        self,
        alert_id: str,
    ) -> Alert:

        alert = self._get(alert_id)

        if alert.status == AlertStatus.RESOLVED:
            raise ValueError(
                "Alert is already resolved."
            )

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()

        return alert

    def list_open(self) -> List[Alert]:

        return [
            alert
            for alert in self._alerts.values()
            if alert.status != AlertStatus.RESOLVED
        ]

    def history(self) -> List[Alert]:

        return list(
            self._alerts.values()
        )

    def _get(
        self,
        alert_id: str,
    ) -> Alert:

        alert = self.get(alert_id)

        if alert is None:
            raise ValueError(
                f"Alert not found: {alert_id}"
            )

        return alert