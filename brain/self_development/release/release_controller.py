from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from brain.self_development.policy.release_policy import (
    ReleasePolicy,
)
from brain.self_development.release.release_manager import (
    ReleaseManager,
    Release,
)



@dataclass(frozen=True)
class ReleaseControllerResult:
    """
    Result of a controlled release-controller operation.
    """

    success: bool
    release_id: str
    status: str
    message: str
    completed_at: datetime


class ReleaseController:
    """
    Coordinates release eligibility and release lifecycle.

    Responsibilities:
    - evaluate release evidence against policy
    - create release records
    - approve eligible releases
    - record successful releases
    - record failures
    - record rollback state

    It does NOT:
    - generate code
    - modify source code
    - bypass release policy
    - execute arbitrary deployment commands
    """

    def __init__(
        self,
        release_policy: ReleasePolicy,
        release_manager: ReleaseManager,
    ):
        if release_policy is None:
            raise ValueError(
                "Release policy cannot be None."
            )

        if release_manager is None:
            raise ValueError(
                "Release manager cannot be None."
            )

        self.release_policy = release_policy
        self.release_manager = release_manager

    def create_release(
        self,
        candidate_id: str,
        version: str,
    ) -> Release:

        if not candidate_id.strip():
            raise ValueError(
                "Candidate ID cannot be empty."
            )

        if not version.strip():
            raise ValueError(
                "Version cannot be empty."
            )

        return self.release_manager.create(
            candidate_id=candidate_id,
            version=version,
        )

    def approve_release(
        self,
        release_id: str,
        evidence: Dict,
    ) -> ReleaseControllerResult:

        if evidence is None:
            raise ValueError(
                "Release evidence cannot be None."
            )

        decision = self.release_policy.evaluate(
            evidence
        )

        if not decision.eligible:
            return ReleaseControllerResult(
                success=False,
                release_id=release_id,
                status="rejected",
                message=(
                    "Release is not eligible: "
                    + "; ".join(decision.reasons)
                ),
                completed_at=datetime.utcnow(),
            )

        release = self.release_manager.approve(
            release_id=release_id,
            evidence=evidence,
        )

        return ReleaseControllerResult(
            success=True,
            release_id=release.release_id,
            status=release.status.value,
            message="Release approved by policy.",
            completed_at=datetime.utcnow(),
        )

    def mark_released(
        self,
        release_id: str,
    ) -> ReleaseControllerResult:

        release = self.release_manager.mark_released(
            release_id
        )

        return ReleaseControllerResult(
            success=True,
            release_id=release.release_id,
            status=release.status.value,
            message="Release recorded as successful.",
            completed_at=datetime.utcnow(),
        )

    def mark_failed(
        self,
        release_id: str,
        evidence: Dict = None,
    ) -> ReleaseControllerResult:

        release = self.release_manager.mark_failed(
            release_id=release_id,
            evidence=evidence,
        )

        return ReleaseControllerResult(
            success=True,
            release_id=release.release_id,
            status=release.status.value,
            message="Release failure recorded.",
            completed_at=datetime.utcnow(),
        )

    def mark_rolled_back(
        self,
        release_id: str,
    ) -> ReleaseControllerResult:

        release = self.release_manager.mark_rolled_back(
            release_id
        )

        return ReleaseControllerResult(
            success=True,
            release_id=release.release_id,
            status=release.status.value,
            message="Release rollback recorded.",
            completed_at=datetime.utcnow(),
        )