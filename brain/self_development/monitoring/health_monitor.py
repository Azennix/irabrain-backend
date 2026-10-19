from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class HealthStatus(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class HealthReport:
    """
    Represents the observed health of an IRABRAIN version.
    """

    target_id: str
    status: HealthStatus
    metrics: Dict[str, float] = field(
        default_factory=dict
    )
    message: str = ""
    checked_at: datetime = field(
        default_factory=datetime.utcnow
    )


class HealthMonitor:
    """
    Monitors the runtime health of a development candidate
    or released version.

    Responsibilities:
    - receive health metrics
    - evaluate configured thresholds
    - produce structured health reports
    - provide the latest health state

    It does NOT:
    - modify source code
    - deploy versions
    - perform rollback itself
    - make release decisions
    """

    def __init__(
        self,
        thresholds: Optional[Dict[str, float]] = None,
    ):
        self.thresholds = (
            dict(thresholds)
            if thresholds is not None
            else {}
        )

        self._latest_reports: Dict[
            str, HealthReport
        ] = {}

    def check(
        self,
        target_id: str,
        metrics: Dict[str, float],
    ) -> HealthReport:

        if not target_id.strip():
            raise ValueError(
                "Target ID cannot be empty."
            )

        if metrics is None:
            raise ValueError(
                "Health metrics cannot be None."
            )

        status = HealthStatus.HEALTHY
        degraded_metrics = []

        for metric, value in metrics.items():

            threshold = self.thresholds.get(
                metric
            )

            if threshold is not None and value > threshold:
                degraded_metrics.append(metric)

        if degraded_metrics:
            status = HealthStatus.DEGRADED

        message = (
            "Health check passed."
            if status == HealthStatus.HEALTHY
            else (
                "Health degradation detected in: "
                + ", ".join(degraded_metrics)
            )
        )

        report = HealthReport(
            target_id=target_id,
            status=status,
            metrics=dict(metrics),
            message=message,
        )

        self._latest_reports[target_id] = report

        return report

    def get_latest(
        self,
        target_id: str,
    ) -> Optional[HealthReport]:

        return self._latest_reports.get(
            target_id
        )