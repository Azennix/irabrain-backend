from dataclasses import dataclass

from brain.self_development.integration.core_execution_signal import (
    CoreExecutionSignal,
)
from brain.self_development.intelligence.hypothesis_evaluator import (
    SelfDevelopmentHypothesisEvaluator,
)
from brain.self_development.intelligence.hypothesis_generator import (
    SelfDevelopmentHypothesisGenerator,
)
from brain.self_development.intelligence.improvement_candidate import (
    ImprovementCandidate,
)
from brain.self_development.intelligence.improvement_candidate_builder import (
    SelfDevelopmentImprovementCandidateBuilder,
)
from brain.self_development.intelligence.investigation_outcome_normalizer import (
    InvestigationOutcomeNormalizer,
)
from brain.self_development.intelligence.investigation_pipeline import (
    SelfDevelopmentInvestigationPipeline,
)


@dataclass(frozen=True)
class ImprovementIntelligenceResult:
    investigation_requested: bool
    candidate: ImprovementCandidate | None


class SelfDevelopmentImprovementIntelligencePipeline:
    """
    Complete Intelligence flow from a Core signal
    to a validated improvement candidate.

    Flow:

        Core Signal
            ↓
        Investigation
            ↓
        Outcome
            ↓
        Hypothesis
            ↓
        Evaluation
            ↓
        Improvement Candidate

    This pipeline does not execute development.
    """

    def __init__(
        self,
        investigation_pipeline: SelfDevelopmentInvestigationPipeline,
        outcome_normalizer: InvestigationOutcomeNormalizer | None = None,
        hypothesis_generator: SelfDevelopmentHypothesisGenerator | None = None,
        hypothesis_evaluator: SelfDevelopmentHypothesisEvaluator | None = None,
        candidate_builder: SelfDevelopmentImprovementCandidateBuilder | None = None,
    ):
        if investigation_pipeline is None:
            raise ValueError(
                "Investigation pipeline cannot be None."
            )

        self.investigation_pipeline = investigation_pipeline
        self.outcome_normalizer = (
            outcome_normalizer
            or InvestigationOutcomeNormalizer()
        )
        self.hypothesis_generator = (
            hypothesis_generator
            or SelfDevelopmentHypothesisGenerator()
        )
        self.hypothesis_evaluator = (
            hypothesis_evaluator
            or SelfDevelopmentHypothesisEvaluator()
        )
        self.candidate_builder = (
            candidate_builder
            or SelfDevelopmentImprovementCandidateBuilder()
        )

    def process(
        self,
        signal: CoreExecutionSignal,
    ) -> ImprovementIntelligenceResult:
        if signal is None:
            raise ValueError(
                "Core execution signal cannot be None."
            )

        investigation_result = (
            self.investigation_pipeline.process(signal)
        )

        if not investigation_result.investigation_requested:
            return ImprovementIntelligenceResult(
                investigation_requested=False,
                candidate=None,
            )

        outcome = self.outcome_normalizer.normalize(
            investigation_result.interpretation
        )

        hypothesis = self.hypothesis_generator.generate(
            outcome
        )

        if hypothesis is None:
            return ImprovementIntelligenceResult(
                investigation_requested=True,
                candidate=None,
            )

        evaluation = self.hypothesis_evaluator.evaluate(
            hypothesis
        )

        candidate = self.candidate_builder.build(
            hypothesis,
            evaluation,
        )

        return ImprovementIntelligenceResult(
            investigation_requested=True,
            candidate=candidate,
        )