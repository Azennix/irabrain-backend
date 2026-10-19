from brain.self_development.integration.core_execution_signal import (
    CoreExecutionSignal,
)
from brain.self_development.intelligence.foundation_adapter import (
    SelfDevelopmentFoundationAdapter,
)
from brain.self_development.intelligence.investigation_pipeline import (
    SelfDevelopmentInvestigationPipeline,
)
from brain.self_development.intelligence.intelligence_policy import (
    SelfDevelopmentIntelligencePolicy,
)


class SafeSelfDevelopmentInvestigationPipeline:
    """
    Safety wrapper around the Intelligence investigation pipeline.

    Intelligence is allowed to observe, investigate, and interpret.
    It is never allowed to execute development or release actions.
    """

    def __init__(
        self,
        foundation_adapter: SelfDevelopmentFoundationAdapter,
        intelligence_policy: SelfDevelopmentIntelligencePolicy | None = None,
    ):
        if foundation_adapter is None:
            raise ValueError(
                "Foundation adapter cannot be None."
            )

        self.foundation_adapter = foundation_adapter

        self.intelligence_policy = (
            intelligence_policy
            or SelfDevelopmentIntelligencePolicy()
        )

        self.pipeline = SelfDevelopmentInvestigationPipeline(
            foundation_adapter=foundation_adapter,
        )

    def process(
        self,
        signal: CoreExecutionSignal,
    ):
        investigation_decision = (
            self.intelligence_policy.authorize(
                "investigation"
            )
        )

        if not investigation_decision.allowed:
            raise PermissionError(
                investigation_decision.reason
            )

        return self.pipeline.process(signal)

    def authorize_action(self, action: str):
        return self.intelligence_policy.authorize(action)