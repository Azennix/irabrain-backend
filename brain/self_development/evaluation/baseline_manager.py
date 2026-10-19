from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass(frozen=True)
class Baseline:
    """
    Represents a known-good performance baseline
    for an IRABRAIN capability set.
    """

    baseline_id: str
    metrics: Dict[str, float]
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class BaselineManager:
    """
    Manages known performance baselines.

    Responsibilities:
    - create baselines
    - store baselines
    - retrieve baselines
    - replace a baseline when explicitly authorized

    It does NOT:
    - modify source code
    - execute development
    - decide whether a candidate should be released
    - automatically promote candidates
    """

    def __init__(self):
        self._baselines: Dict[str, Baseline] = {}

    def create(
        self,
        baseline_id: str,
        metrics: Dict[str, float],
    ) -> Baseline:

        if not baseline_id.strip():
            raise ValueError(
                "Baseline ID cannot be empty."
            )

        if not metrics:
            raise ValueError(
                "Baseline metrics cannot be empty."
            )

        for name, value in metrics.items():

            if not name.strip():
                raise ValueError(
                    "Metric name cannot be empty."
                )

            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"Metric '{name}' must be numeric."
                )

        baseline = Baseline(
            baseline_id=baseline_id,
            metrics=dict(metrics),
        )

        self._baselines[baseline_id] = baseline

        return baseline

    def get(
        self,
        baseline_id: str,
    ) -> Optional[Baseline]:

        return self._baselines.get(
            baseline_id
        )

    def exists(
        self,
        baseline_id: str,
    ) -> bool:

        return baseline_id in self._baselines