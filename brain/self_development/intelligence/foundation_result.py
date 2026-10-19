from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FoundationInvestigationResult:
    """
    Result returned from the Self-Development Foundation
    to the Intelligence layer.

    This describes the result only.
    It does not grant authorization for further actions.
    """

    success: bool

    status: str

    evidence: dict[str, Any] = field(
        default_factory=dict
    )

    error: str | None = None