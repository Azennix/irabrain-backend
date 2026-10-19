from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from brain.self_development.domain.models import Evidence


@dataclass
class RootCauseHypothesis:
    """
    Represents a possible root cause identified
    from available evidence.
    """

    statement: str
    confidence: float
    supporting_evidence: List[Evidence] = field(
        default_factory=list
    )


@dataclass
class RootCauseAnalysis:
    """
    Result of root-cause analysis.
    """

    improvement_id: str
    hypotheses: List[RootCauseHypothesis]
    analyzed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class RootCauseAnalyzer:
    """
    Analyzes collected evidence and produces
    structured root-cause hypotheses.

    Responsibilities:
    - inspect evidence
    - group evidence logically
    - produce possible root causes
    - assign confidence to hypotheses

    It does NOT:
    - modify source code
    - execute development
    - run tests
    - deploy changes
    - make release decisions

    Deeper reasoning can later be provided by
    an intelligence/LLM layer without changing
    this component's interface.
    """

    def analyze(
        self,
        improvement_id: str,
        evidence: List[Evidence],
    ) -> RootCauseAnalysis:

        if not improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )

        if not evidence:
            raise ValueError(
                "Evidence is required for root-cause analysis."
            )

        hypotheses = []

        # -------------------------------------------------
        # Evidence-backed analysis
        # -------------------------------------------------

        hypotheses.append(
            RootCauseHypothesis(
                statement=(
                    "The observed improvement signal may "
                    "be caused by an underlying system "
                    "condition represented in the collected evidence."
                ),
                confidence=0.5,
                supporting_evidence=list(evidence),
            )
        )

        return RootCauseAnalysis(
            improvement_id=improvement_id,
            hypotheses=hypotheses,
        )