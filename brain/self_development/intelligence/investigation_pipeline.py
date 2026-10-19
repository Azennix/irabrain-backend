from dataclasses import dataclass
from typing import Any

from brain.self_development.integration.core_execution_signal import (
    CoreExecutionSignal,
)
from brain.self_development.intelligence.foundation_adapter import (
    SelfDevelopmentFoundationAdapter,
)
from brain.self_development.intelligence.investigation_request import (
    InvestigationRequest,
)
from brain.self_development.intelligence.investigation_result_interpreter import (
    InvestigationInterpretation,
    InvestigationResultInterpreter,
)
from brain.self_development.intelligence.intelligence_pipeline import (
    SelfDevelopmentIntelligencePipeline,
)


@dataclass(frozen=True)
class InvestigationPipelineResult:
    investigation_requested: bool
    request: InvestigationRequest | None
    interpretation: InvestigationInterpretation | None


class SelfDevelopmentInvestigationPipeline:
    """
    Coordinates the boundary between:

    Core signal
        -> Intelligence
        -> Foundation investigation
        -> Intelligence interpretation

    This coordinator does not authorize or execute improvements.
    """

    def __init__(
        self,
        intelligence_pipeline: SelfDevelopmentIntelligencePipeline | None = None,
        foundation_adapter: SelfDevelopmentFoundationAdapter | None = None,
        result_interpreter: InvestigationResultInterpreter | None = None,
    ):
        self.intelligence_pipeline = (
            intelligence_pipeline
            or SelfDevelopmentIntelligencePipeline()
        )

        self.foundation_adapter = foundation_adapter

        self.result_interpreter = (
            result_interpreter
            or InvestigationResultInterpreter()
        )

    def process(
        self,
        signal: CoreExecutionSignal,
    ) -> InvestigationPipelineResult:

        request = self.intelligence_pipeline.process(signal)

        if request is None:
            return InvestigationPipelineResult(
                investigation_requested=False,
                request=None,
                interpretation=None,
            )

        if self.foundation_adapter is None:
            raise RuntimeError(
                "Foundation adapter is required for investigation."
            )

        foundation_result = self.foundation_adapter.investigate(
            request
        )

        interpretation = self.result_interpreter.interpret(
            foundation_result
        )

        return InvestigationPipelineResult(
            investigation_requested=True,
            request=request,
            interpretation=interpretation,
        )