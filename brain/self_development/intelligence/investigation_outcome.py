from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InvestigationOutcome:
    """
    Normalized outcome of the Self-Development
    investigation stage.

    This represents information only.
    It does not authorize or execute any action.
    """

    status: str
    actionable: bool
    reason: str
    evidence: dict[str, Any]

    @property
    def requires_follow_up(self) -> bool:
        return self.status == "completed" and self.actionable