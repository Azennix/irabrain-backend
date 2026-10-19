from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass(frozen=True)
class RollbackResult:
    """
    Result of a rollback operation.
    """

    success: bool
    candidate_id: str
    target_version: str
    reason: str
    message: str
    completed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class RollbackManager:
    """
    Manages controlled rollback operations.

    Responsibilities:
    - identify a known-good target version
    - validate rollback requests
    - record rollback operations
    - return structured rollback results

    It does NOT:
    - modify source code directly
    - bypass release policy
    - deploy arbitrary versions
    - decide when rollback is required
    """

    def __init__(self):
        self._known_good_versions: Dict[
            str, str
        ] = {}

        self._rollback_history = []

    def register_known_good_version(
        self,
        version: str,
        reference: str,
    ) -> None:

        if not version.strip():
            raise ValueError(
                "Version cannot be empty."
            )

        if not reference.strip():
            raise ValueError(
                "Version reference cannot be empty."
            )

        self._known_good_versions[
            version
        ] = reference

    def rollback(
        self,
        candidate_id: str,
        target_version: str,
        reason: str,
    ) -> RollbackResult:

        if not candidate_id.strip():
            raise ValueError(
                "Candidate ID cannot be empty."
            )

        if not target_version.strip():
            raise ValueError(
                "Target version cannot be empty."
            )

        if not reason.strip():
            raise ValueError(
                "Rollback reason cannot be empty."
            )

        if target_version not in (
            self._known_good_versions
        ):
            raise ValueError(
                f"Target version is not registered "
                f"as known-good: {target_version}"
            )

        result = RollbackResult(
            success=True,
            candidate_id=candidate_id,
            target_version=target_version,
            reason=reason,
            message=(
                f"Rollback to {target_version} "
                "is authorized and recorded."
            ),
        )

        self._rollback_history.append(result)

        return result

    def get_known_good_reference(
        self,
        version: str,
    ) -> Optional[str]:

        return self._known_good_versions.get(
            version
        )

    def history(self):

        return list(self._rollback_history)