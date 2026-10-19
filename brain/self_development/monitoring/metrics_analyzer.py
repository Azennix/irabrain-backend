from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass(frozen=True)
class MetricTrend:
    """
    Represents the trend of one metric.
    """

    metric: str
    first_value: float
    latest_value: float
    difference: float
    direction: str


@dataclass(frozen=True)
class MetricsAnalysis:
    """
    Structured analysis of runtime metrics.
    """

    target_id: str
    trends: List[MetricTrend] = field(
        default_factory=list
    )
    degraded_metrics: List[str] = field(
        default_factory=list
    )
    analyzed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class MetricsAnalyzer:
    """
    Analyzes historical runtime metrics.

    Responsibilities:
    - compare metric observations
    - identify increasing/decreasing trends
    - identify degraded metrics
    - produce structured monitoring evidence

    It does NOT:
    - modify source code
    - deploy versions
    - perform rollback
    - make release decisions
    """

    def __init__(
        self,
        degradation_threshold: float = 0.0,
    ):
        if degradation_threshold < 0:
            raise ValueError(
                "Degradation threshold cannot be negative."
            )

        self.degradation_threshold = (
            degradation_threshold
        )

    def analyze(
        self,
        target_id: str,
        history: List[Dict[str, float]],
    ) -> MetricsAnalysis:

        if not target_id.strip():
            raise ValueError(
                "Target ID cannot be empty."
            )

        if not history:
            raise ValueError(
                "Metric history cannot be empty."
            )

        first = history[0]
        latest = history[-1]

        trends = []
        degraded_metrics = []

        for metric in first:

            if metric not in latest:
                continue

            first_value = first[metric]
            latest_value = latest[metric]

            difference = (
                latest_value - first_value
            )

            if difference > self.degradation_threshold:
                direction = "increasing"
            elif difference < -self.degradation_threshold:
                direction = "decreasing"
            else:
                direction = "stable"

            if (
                difference
                > self.degradation_threshold
            ):
                degraded_metrics.append(metric)

            trends.append(
                MetricTrend(
                    metric=metric,
                    first_value=first_value,
                    latest_value=latest_value,
                    difference=difference,
                    direction=direction,
                )
            )

        return MetricsAnalysis(
            target_id=target_id,
            trends=trends,
            degraded_metrics=degraded_metrics,
        )