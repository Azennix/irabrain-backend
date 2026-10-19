from brain.base.brain_request import BrainRequest
from brain.tools.tool_trigger_decision import ToolTriggerDecision
from decision.intent_result import IntentResult, IntentType

import re


class ToolTriggerAnalyzer:
    """
    Determines whether the current request should enter
    the tool system.

    This layer handles deterministic tool requirements
    before any LLM-based decision is made.
    """

    def analyze(
        self,
        request: BrainRequest,
        intent_result: IntentResult
    ) -> ToolTriggerDecision:

        text = request.query.strip()

        # ==========================================
        # EMPTY REQUEST
        # ==========================================

        if not text:

            return ToolTriggerDecision(
                should_use_tools=False,
                confidence=1.0,
                reason="Empty request."
            )

        # ==========================================
        # EXPLICIT TOOL REQUIREMENT
        # ==========================================

        if intent_result.requires_tool:

            return ToolTriggerDecision(
                should_use_tools=True,
                confidence=intent_result.confidence,
                reason="Intent explicitly requires a tool."
            )

        # ==========================================
        # EXACT ARITHMETIC
        # ==========================================

        if self._requires_calculator(text):

            return ToolTriggerDecision(
                should_use_tools=True,
                confidence=1.0,
                reason="Exact numerical calculation requires calculator."
            )

        # ==========================================
        # NORMAL CONVERSATION
        # ==========================================

        if intent_result.intent == IntentType.CONVERSATION:

            return ToolTriggerDecision(
                should_use_tools=False,
                confidence=intent_result.confidence,
                reason="Normal conversation does not require tools."
            )

        # ==========================================
        # MEMORY
        # ==========================================

        if intent_result.intent == IntentType.MEMORY:

            return ToolTriggerDecision(
                should_use_tools=False,
                confidence=intent_result.confidence,
                reason="Memory operation does not require tools."
            )

        # ==========================================
        # MEMORY MANAGEMENT
        # ==========================================

        if intent_result.intent == IntentType.MEMORY_MANAGEMENT:

            return ToolTriggerDecision(
                should_use_tools=False,
                confidence=intent_result.confidence,
                reason="Memory management is handled by the memory subsystem."
            )

        # ==========================================
        # INFORMATION
        # ==========================================

        if intent_result.intent == IntentType.INFORMATION:

            return ToolTriggerDecision(
                should_use_tools=False,
                confidence=intent_result.confidence,
                reason="Information request does not automatically require tools."
            )

        # ==========================================
        # TASK
        # ==========================================

        if intent_result.intent == IntentType.TASK:

            return ToolTriggerDecision(
                should_use_tools=False,
                confidence=intent_result.confidence,
                reason="Task may require reasoning; tool requirement has not yet been established."
            )

        # ==========================================
        # FALLBACK
        # ==========================================

        return ToolTriggerDecision(
            should_use_tools=False,
            confidence=0.0,
            reason="Tool requirement could not be established."
        )

    # ==========================================
    # CALCULATOR DETECTION
    # ==========================================

    def _requires_calculator(self, text: str) -> bool:

        normalized = text.lower().strip()

        # ------------------------------------------
        # Explicit calculation language
        # ------------------------------------------

        calculation_words = [
            "calculate",
            "compute",
            "what is",
            "how much",
            "add",
            "subtract",
            "multiply",
            "divide",
            "percentage",
            "percent",
            "square",
            "power"
        ]

        has_calculation_word = any(
            word in normalized
            for word in calculation_words
        )

        # ------------------------------------------
        # Arithmetic operators
        # ------------------------------------------

        has_operator = bool(
            re.search(
                r"\d+(?:\.\d+)?\s*[\+\-\*/x\u00d7\u00f7]\s*\d+",
                normalized
            )
        )

        # ------------------------------------------
        # Direct arithmetic expression
        # ------------------------------------------

        direct_expression = bool(
            re.fullmatch(
                r"\s*\d+(?:\.\d+)?\s*[\+\-\*/x\u00d7\u00f7]\s*\d+(?:\.\d+)?\s*",
                normalized
            )
        )

        # ------------------------------------------
        # Decision
        # ------------------------------------------

        if direct_expression:
            return True

        if has_operator:
            return True

        if has_calculation_word and re.search(
            r"\d",
            normalized
        ):
            return True

        return False