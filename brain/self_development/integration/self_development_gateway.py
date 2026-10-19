from brain.self_development.integration.core_execution_signal import (
    CoreExecutionSignal,
)
from brain.self_development.intelligence.safe_investigation_pipeline import (
    SafeSelfDevelopmentInvestigationPipeline,
)
from brain.self_development.intelligence.investigation_result_interpreter import (
    InvestigationInterpretation,
)


class SelfDevelopmentGateway:
    """
    Stable entry point from IRABRAIN Core into the
    separate Self-Development system.

    The gateway:
    - accepts Core execution signals
    - forwards them into Self-Development Intelligence
    - returns an interpreted investigation result

    It does NOT:
    - modify Core
    - execute development
    - deploy changes
    - release candidates
    - grant authorization
    """

    def __init__(
        self,
       investigation_pipeline: SafeSelfDevelopmentInvestigationPipeline,
    ):
        if investigation_pipeline is None:
            raise ValueError(
                "Self-development investigation pipeline cannot be None."
            )

        self.investigation_pipeline = investigation_pipeline

    def process(
        self,
        signal: CoreExecutionSignal,
    ) -> InvestigationInterpretation | None:
        if signal is None:
            raise ValueError(
                "Core execution signal cannot be None."
            )

        result = self.investigation_pipeline.process(
            signal
        )

        if not result.investigation_requested:
            return None

        return result.interpretation