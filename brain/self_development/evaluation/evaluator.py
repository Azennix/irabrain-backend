from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class EvaluationResult:
    """
    Comparison result between a baseline and candidate.
    """

    baseline_id: str
    candidate_metrics: Dict[str, float]
    baseline_metrics: Dict[str, float]
    improved: bool
    regressed: bool
    score_difference: float
    metric_differences: Dict[str, float] = field(
        default_factory=dict
    )
    evaluated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class Evaluator:
    """
    Evaluates a candidate against a known baseline.

    Responsibilities:
    - compare candidate metrics with baseline metrics
    - calculate metric differences
    - identify improvement
    - identify regression
    - return structured evaluation results

    It does NOT:
    - modify source code
    - modify baselines
    - release candidates
    - deploy changes
    """

    def evaluate(
        self,
        baseline_id: str,
        baseline_metrics: Dict[str, float],
        candidate_metrics: Dict[str, float],
    ) -> EvaluationResult:

        if not baseline_id.strip():
            raise ValueError(
                "Baseline ID cannot be empty."
            )

        if not baseline_metrics:
            raise ValueError(
                "Baseline metrics cannot be empty."
            )

        if not candidate_metrics:
            raise ValueError(
                "Candidate metrics cannot be empty."
            )

        common_metrics = (
            set(baseline_metrics)
            & set(candidate_metrics)
        )

        if not common_metrics:
            raise ValueError(
                "No common metrics available for evaluation."
            )

        metric_differences = {
            metric:
            candidate_metrics[metric]
            - baseline_metrics[metric]
            for metric in common_metrics
        }

        baseline_score = (
            sum(
                baseline_metrics[metric]
                for metric in common_metrics
            )
            / len(common_metrics)
        )

        candidate_score = (
            sum(
                candidate_metrics[metric]
                for metric in common_metrics
            )
            / len(common_metrics)
        )

        score_difference = (
            candidate_score - baseline_score
        )

        improved = score_difference > 0
        regressed = score_difference < 0

        return EvaluationResult(
            baseline_id=baseline_id,
            candidate_metrics=dict(candidate_metrics),
            baseline_metrics=dict(baseline_metrics),
            improved=improved,
            regressed=regressed,
            score_difference=score_difference,
            metric_differences=metric_differences,
        )