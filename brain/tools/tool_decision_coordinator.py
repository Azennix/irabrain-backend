from brain.base.brain_request import BrainRequest
from brain.tools.tool_trigger_analyzer import ToolTriggerAnalyzer
from brain.tools.tool_selector import ToolSelector
from brain.tools.tool_decision import ToolDecision
from brain.tools.tool_registry import ToolRegistry
from decision.intent_result import IntentResult
from brain.llm.memory_llm_service import MemoryLLMService


class ToolDecisionCoordinator:

    """
    Coordinates the complete tool-decision process.

    It does NOT:
    - execute tools
    - validate tool arguments
    - handle permissions
    - perform the actual tool action

    It only coordinates:

        trigger
        ↓
        intelligent trigger
        ↓
        selector
        ↓
        final ToolDecision
    """

    def __init__(
        self,
        registry: ToolRegistry,
        llm_service: MemoryLLMService
    ):

        self.registry = registry
        if llm_service is None:
            raise ValueError(
                "ToolDecisionCoordinator requires an LLM provider."
        )

        self.trigger_analyzer = ToolTriggerAnalyzer()

        self.selector = ToolSelector(
            registry=registry,
            llm_service=llm_service
        )

    def decide(
        self,
        request: BrainRequest,
        intent_result: IntentResult
    ) -> ToolDecision:

        # ==========================================
        # STEP 1 — BASIC TRIGGER
        # ==========================================

        trigger_decision = (
            self.trigger_analyzer.analyze(
                request,
                intent_result
            )
        )

        # ==========================================
        # STEP 2 — IF BASIC TRIGGER SAYS NO
        # ==========================================

        if not trigger_decision.should_use_tools:

             if not intent_result.requires_tool:


                return ToolDecision(
                    requires_tool=False,
                    tool_name=None,
                    confidence=intent_result.confidence,
                    reason="Semantic analysis determined that no tool is required."
            )

        # ==========================================
        # STEP 3 — SELECT TOOL
        # ==========================================

        return self.selector.select(
            request
        )