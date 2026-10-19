from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class StagingStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    VALIDATED = "validated"
    FAILED = "failed"
    CLOSED = "closed"


@dataclass
class StagingEnvironment:
    """
    Represents an isolated staging environment
    for a self-development candidate.
    """

    staging_id: str
    experiment_id: str
    candidate_id: str
    status: StagingStatus = StagingStatus.CREATED
    validation_result: Optional[Dict] = None
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class StagingManager:
    """
    Manages isolated staging environments.

    Responsibilities:
    - create staging environments
    - activate candidates in staging
    - record staging validation
    - mark staging success or failure
    - close staging environments

    It does NOT:
    - deploy to production
    - bypass validation
    - make release decisions
    """

    def __init__(self):
        self._staging: Dict[
            str, StagingEnvironment
        ] = {}
        self._counter = 0

    def create(
        self,
        experiment_id: str,
        candidate_id: str,
    ) -> StagingEnvironment:

        if not experiment_id.strip():
            raise ValueError(
                "Experiment ID cannot be empty."
            )

        if not candidate_id.strip():
            raise ValueError(
                "Candidate ID cannot be empty."
            )

        self._counter += 1

        staging_id = (
            f"STG-{self._counter:04d}"
        )

        environment = StagingEnvironment(
            staging_id=staging_id,
            experiment_id=experiment_id,
            candidate_id=candidate_id,
        )

        self._staging[staging_id] = environment

        return environment

    def activate(
        self,
        staging_id: str,
    ) -> StagingEnvironment:

        environment = self._get(staging_id)

        if environment.status != StagingStatus.CREATED:
            raise ValueError(
                "Only a created staging environment "
                "can be activated."
            )

        environment.status = StagingStatus.ACTIVE

        return environment

    def validate(
        self,
        staging_id: str,
        result: Dict,
    ) -> StagingEnvironment:

        environment = self._get(staging_id)

        if environment.status != StagingStatus.ACTIVE:
            raise ValueError(
                "Only an active staging environment "
                "can be validated."
            )

        environment.validation_result = dict(result)

        if result.get("success") is True:
            environment.status = (
                StagingStatus.VALIDATED
            )
        else:
            environment.status = (
                StagingStatus.FAILED
            )

        return environment

    def close(
        self,
        staging_id: str,
    ) -> StagingEnvironment:

        environment = self._get(staging_id)

        environment.status = StagingStatus.CLOSED

        return environment

    def get(
        self,
        staging_id: str,
    ) -> Optional[StagingEnvironment]:

        return self._staging.get(staging_id)

    def _get(
        self,
        staging_id: str,
    ) -> StagingEnvironment:

        environment = self.get(staging_id)

        if environment is None:
            raise ValueError(
                f"Staging environment not found: "
                f"{staging_id}"
            )

        return environment