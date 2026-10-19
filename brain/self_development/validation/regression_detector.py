from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass(frozen=True)
class Regression:
    """
    Represents a detected regression.
    """

    capability: str
    baseline_value: float
    candidate_value: float
    difference: float
    description: str


@dataclass(frozen=True)
class RegressionReport:
    """
    Result of regression analysis.
    """

    has_regressions: bool
    regressions: List[Regression] = field(
        default_factory=list
    )
    analyzed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class RegressionDetector:
    """
    Detects regressions by comparing a known baseline
    with a candidate evaluation.

    Responsibilities:
    - compare baseline metrics with candidate metrics
    - identify meaningful degradation
    - produce structured regression evidence

    It does NOT:
    - modify code
    - execute development
    - deploy changes
    - make release decisions
    """

    def __init__(
        self,
        tolerance: float = 0.0,
    ):
        if tolerance < 0:
            raise ValueError(
                "Tolerance cannot be negative."
            )

        self.tolerance = tolerance

    def detect(
        self,
        baseline: Dict[str, float],
        candidate: Dict[str, float],
    ) -> RegressionReport:

        if baseline is None:
            raise ValueError(
                "Baseline metrics cannot be None."
            )

        if candidate is None:
            raise ValueError(
                "Candidate metrics cannot be None."
            )

        regressions = []

        for capability, baseline_value in baseline.items():

            if capability not in candidate:
                continue

            candidate_value = candidate[
                capability
            ]

            difference = (
                candidate_value - baseline_value
            )

            if difference < -self.tolerance:

                regressions.append(
                    Regression(
                        capability=capability,
                        baseline_value=baseline_value,
                        candidate_value=candidate_value,
                        difference=difference,
                        description=(
                            f"{capability} degraded from "
                            f"{baseline_value} to "
                            f"{candidate_value}."
                        ),
                    )
                )

        return RegressionReport(
            has_regressions=bool(regressions),
            regressions=regressions,
        )