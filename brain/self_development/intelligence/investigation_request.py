from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InvestigationRequest:
    """
    Request for Self-Development investigation.

    This only describes what should be investigated.
    It does not execute investigation or authorize changes.
    """

    observation_id: str
    operation: str
    reason: str
    evidence: dict[str, Any]