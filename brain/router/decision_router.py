from brain.memory.message_analysis_result import MessageAnalysisResult
from decision.intent_result import IntentResult
from brain.tools.tool_decision import ToolDecision


class DecisionRouter:

    def route(
        self,
        analysis: MessageAnalysisResult,
        intent: IntentResult,
        tool_decision: ToolDecision
    ) -> list[str]:

        routes = []

        # =========================================
        # MEMORY
        # =========================================

        if (
            analysis.should_enter_memory_pipeline
            or intent.requires_memory
        ):
            routes.append("memory")
        # =========================================
        # REASONING
        # =========================================

        if intent.requires_reasoning:
            routes.append("reasoning")

        # =========================================
        # TOOL
        # =========================================

        if intent.requires_tool or tool_decision.requires_tool:
            routes.append("tool")

        # =========================================
        # LLM
        # =========================================

        if analysis.requires_llm:
            routes.append("llm")

        return routes