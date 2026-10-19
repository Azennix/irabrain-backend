from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ImprovementCandidate:
    """
    A validated candidate for further self-development planning.

    This is still a proposal.

    It does not:
    - execute development
    - modify code
    - authorize changes
    - deploy or release anything
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
                "Candidate statement cannot be empty."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Candidate confidence must be between 0 and 1."
            )