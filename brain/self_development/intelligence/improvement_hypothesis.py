from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ImprovementHypothesis:
    """
    Candidate improvement identified by the
    Self-Development Intelligence layer.

    This is a hypothesis only.

    It does not:
    - modify code
    - authorize changes
    - execute development
    - release anything
    """

    hypothesis_id: str
    statement: str
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.hypothesis_id.strip():
            raise ValueError(
                "Hypothesis ID cannot be empty."
            )

        if not self.statement.strip():
            raise ValueError(
                "Hypothesis statement cannot be empty."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Hypothesis confidence must be between 0 and 1."
            )