from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class ReleaseStatus(str, Enum):
    CREATED = "created"
    APPROVED = "approved"
    RELEASED = "released"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Release:
    """
    Represents a controlled release of a candidate.
    """

    release_id: str
    candidate_id: str
    version: str
    status: ReleaseStatus = ReleaseStatus.CREATED
    evidence: Optional[Dict] = None
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )
    completed_at: Optional[datetime] = None


class ReleaseManager:
    """
    Manages the lifecycle of an authorized release.

    Responsibilities:
    - create release records
    - approve an already-authorized release
    - record successful releases
    - record release failures
    - record rollback state

    It does NOT:
    - generate code
    - bypass release policy
    - decide whether a candidate is safe
    - directly deploy arbitrary code
    """

    def __init__(self):
        self._releases: Dict[
            str, Release
        ] = {}

        self._counter = 0

    def create(
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

        self._counter += 1

        release_id = (
            f"REL-{self._counter:04d}"
        )

        release = Release(
            release_id=release_id,
            candidate_id=candidate_id,
            version=version,
        )

        self._releases[release_id] = release

        return release

    def approve(
        self,
        release_id: str,
        evidence: Dict,
    ) -> Release:

        release = self._get(release_id)

        if release.status != ReleaseStatus.CREATED:
            raise ValueError(
                "Only a created release can be approved."
            )

        release.evidence = dict(evidence)
        release.status = ReleaseStatus.APPROVED

        return release

    def mark_released(
        self,
        release_id: str,
    ) -> Release:

        release = self._get(release_id)

        if release.status != ReleaseStatus.APPROVED:
            raise ValueError(
                "Only an approved release can be released."
            )

        release.status = ReleaseStatus.RELEASED
        release.completed_at = datetime.utcnow()

        return release

    def mark_failed(
        self,
        release_id: str,
        evidence: Optional[Dict] = None,
    ) -> Release:

        release = self._get(release_id)

        release.evidence = (
            dict(evidence)
            if evidence is not None
            else release.evidence
        )

        release.status = ReleaseStatus.FAILED
        release.completed_at = datetime.utcnow()

        return release

    def mark_rolled_back(
        self,
        release_id: str,
    ) -> Release:

        release = self._get(release_id)

        release.status = ReleaseStatus.ROLLED_BACK
        release.completed_at = datetime.utcnow()

        return release

    def get(
        self,
        release_id: str,
    ) -> Optional[Release]:

        return self._releases.get(
            release_id
        )

    def _get(
        self,
        release_id: str,
    ) -> Release:

        release = self.get(release_id)

        if release is None:
            raise ValueError(
                f"Release not found: {release_id}"
            )

        return release