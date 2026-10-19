from brain.self_development.intelligence.hypothesis_evaluator import (
    HypothesisEvaluation,
)
from brain.self_development.intelligence.improvement_candidate import (
    ImprovementCandidate,
)
from brain.self_development.intelligence.improvement_hypothesis import (
    ImprovementHypothesis,
)


class SelfDevelopmentImprovementCandidateBuilder:
    """
    Converts a sufficiently supported hypothesis into an
    ImprovementCandidate.

    This is still a proposal boundary.

    It does not:
    - create a development plan
    - execute changes
    - authorize actions
    - deploy or release anything
    """

    def build(
        self,
        hypothesis: ImprovementHypothesis,
        evaluation: HypothesisEvaluation,
    ) -> ImprovementCandidate | None:
        if hypothesis is None:
            raise ValueError(
                "Improvement hypothesis cannot be None."
            )

        if evaluation is None:
            raise ValueError(
                "Hypothesis evaluation cannot be None."
            )

        if evaluation.hypothesis_id != hypothesis.hypothesis_id:
            raise ValueError(
                "Hypothesis and evaluation IDs do not match."
            )

        if not evaluation.supported:
            return None

        return ImprovementCandidate(
            candidate_id=f"CAND-{hypothesis.hypothesis_id}",
            hypothesis_id=hypothesis.hypothesis_id,
            statement=hypothesis.statement,
            confidence=evaluation.confidence,
            evidence=dict(hypothesis.evidence),
        )