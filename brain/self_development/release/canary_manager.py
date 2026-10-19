from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class CanaryStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    PASSED = "passed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class CanaryDeployment:
    """
    Represents a controlled canary deployment.
    """

    canary_id: str
    staging_id: str
    candidate_id: str
    traffic_percentage: float
    status: CanaryStatus = CanaryStatus.CREATED
    metrics: Optional[Dict] = None
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class CanaryManager:
    """
    Manages controlled canary deployments.

    Responsibilities:
    - create canary deployments
    - activate a candidate for limited traffic
    - record canary metrics
    - mark canary success or failure
    - stop a canary deployment

    It does NOT:
    - perform unrestricted production deployment
    - bypass release policy
    - modify source code
    - decide final production release
    """

    def __init__(self):
        self._canaries: Dict[
            str, CanaryDeployment
        ] = {}

        self._counter = 0

    def create(
        self,
        staging_id: str,
        candidate_id: str,
        traffic_percentage: float = 5.0,
    ) -> CanaryDeployment:

        if not staging_id.strip():
            raise ValueError(
                "Staging ID cannot be empty."
            )

        if not candidate_id.strip():
            raise ValueError(
                "Candidate ID cannot be empty."
            )

        if not 0 < traffic_percentage <= 100:
            raise ValueError(
                "Traffic percentage must be "
                "greater than 0 and at most 100."
            )

        self._counter += 1

        canary_id = (
            f"CNY-{self._counter:04d}"
        )

        canary = CanaryDeployment(
            canary_id=canary_id,
            staging_id=staging_id,
            candidate_id=candidate_id,
            traffic_percentage=traffic_percentage,
        )

        self._canaries[canary_id] = canary

        return canary

    def activate(
        self,
        canary_id: str,
    ) -> CanaryDeployment:

        canary = self._get(canary_id)

        if canary.status != CanaryStatus.CREATED:
            raise ValueError(
                "Only a created canary can be activated."
            )

        canary.status = CanaryStatus.ACTIVE

        return canary

    def evaluate(
        self,
        canary_id: str,
        metrics: Dict,
    ) -> CanaryDeployment:

        canary = self._get(canary_id)

        if canary.status != CanaryStatus.ACTIVE:
            raise ValueError(
                "Only an active canary can be evaluated."
            )

        canary.metrics = dict(metrics)

        if metrics.get("success") is True:
            canary.status = CanaryStatus.PASSED
        else:
            canary.status = CanaryStatus.FAILED

        return canary

    def stop(
        self,
        canary_id: str,
    ) -> CanaryDeployment:

        canary = self._get(canary_id)

        if canary.status != CanaryStatus.ACTIVE:
            raise ValueError(
                "Only an active canary can be stopped."
            )

        canary.status = CanaryStatus.STOPPED

        return canary

    def get(
        self,
        canary_id: str,
    ) -> Optional[CanaryDeployment]:

        return self._canaries.get(canary_id)

    def _get(
        self,
        canary_id: str,
    ) -> CanaryDeployment:

        canary = self.get(canary_id)

        if canary is None:
            raise ValueError(
                f"Canary deployment not found: {canary_id}"
            )

        return canary