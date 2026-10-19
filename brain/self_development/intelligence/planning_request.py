from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ImprovementPlanningRequest:
    """
    Request handed from Self-Development Intelligence
    to the Foundation planning boundary.

    This is a handoff contract only.
    It does not authorize or execute development.
    """

    candidate_id: str
    hypothesis_id: str
    statement: str
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.candidate_id.strip():
            raise ValueError(
                "Candidate ID cannot be empty."
            )

        if not self.hypothesis_id.strip():
            raise ValueError(
                "Hypothesis ID cannot be empty."
            )

        if not self.statement.strip():
            raise ValueError(
                "Planning statement cannot be empty."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Planning confidence must be between 0 and 1."
            )