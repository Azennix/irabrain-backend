from brain.self_development.integration.core_execution_signal import (
    CoreExecutionSignal,
)
from brain.self_development.intelligence.observer import (
    SelfDevelopmentObserver,
)
from brain.self_development.intelligence.significance_evaluator import (
    SelfDevelopmentSignificanceEvaluator,
)
from brain.self_development.intelligence.investigator import (
    SelfDevelopmentInvestigator,
)
from brain.self_development.intelligence.investigation_request import (
    InvestigationRequest,
)


class SelfDevelopmentIntelligencePipeline:
    """
    Coordinates the initial Self-Development intelligence flow.

    This layer interprets Core signals only.
    It does not execute Foundation actions.
    """

    def __init__(
        self,
        observer: SelfDevelopmentObserver | None = None,
        significance_evaluator: (
            SelfDevelopmentSignificanceEvaluator | None
        ) = None,
        investigator: SelfDevelopmentInvestigator | None = None,
    ):
        self.observer = (
            observer or SelfDevelopmentObserver()
        )

        self.significance_evaluator = (
            significance_evaluator
            or SelfDevelopmentSignificanceEvaluator()
        )

        self.investigator = (
            investigator or SelfDevelopmentInvestigator()
        )

    def process(
        self,
        signal: CoreExecutionSignal,
    ) -> InvestigationRequest | None:

        observation = self.observer.observe(signal)

        decision = self.significance_evaluator.evaluate(
            observation
        )

        return self.investigator.create_request(
            observation=observation,
            decision=decision,
        )