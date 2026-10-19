from brain.base.brain_request import BrainRequest
from brain.llm.memory_llm_service import MemoryLLMService
from brain.tools.tool_trigger_decision import ToolTriggerDecision
from decision.intent_result import IntentResult


class IntelligentToolTrigger:

    """
    Determines whether a user request actually requires
    external tool execution.

    It does NOT:
    - select a tool
    - execute a tool
    - validate a tool
    - handle permissions

    It only determines whether tools are required.
    """

    def __init__(
        self,
        llm_service: MemoryLLMService | None = None
    ):
        if llm_service is None:
            raise ValueError(
              "IntelligentToolTrigger requires an LLM provider."
    )

        self.llm_service = llm_service

    def analyze(
        self,
        request: BrainRequest,
        intent_result: IntentResult
    ) -> ToolTriggerDecision:

        prompt = f"""
Determine whether the user's request requires an external
tool to complete.

Return ONLY valid JSON.

Required format:

{{
    "should_use_tools": false,
    "confidence": 0.95,
    "reason": "The calculation can be performed using the model's existing knowledge."
}}

Rules:

- Exact arithmetic calculations should use the calculator tool.
- Do not rely on the language model's internal arithmetic for exact numerical calculations.
- If the request asks to calculate, compute, multiply, divide, add, subtract, calculate percentages, powers, or similar numerical operations, set should_use_tools=true.

- Use tools when the request requires an external action,
  calculation, live information, search, file operation,
  API call, or another capability unavailable from normal
  language-model reasoning.

- Do NOT use tools for normal conversation.

- Do NOT use tools when the model can answer using its
  existing knowledge and reasoning.

- Do NOT select a specific tool.
  Only decide whether tools are required.

  IMPORTANT RULE
  - Simple casual arithmetic may be answered directly.
- Use the calculator for financial, business, budgeting,
  runway, pricing, profit, revenue, percentage,
  unit-economics, or other decision-relevant calculations.
- If the numerical result could materially influence a
  financial or business decision, prefer the calculator.
- Do not execute the calculation yourself when the calculator
  is selected.

User message:

{request.query}

Detected intent:

{intent_result.intent.value}
"""

        result = self.llm_service.generate_structured(
            prompt=prompt,
            temperature=0.0
        )

        return ToolTriggerDecision(
            should_use_tools=bool(
                result.get(
                    "should_use_tools",
                    False
                )
            ),
            confidence=float(
                result.get(
                    "confidence",
                    0.5
                )
            ),
            reason=result.get(
                "reason",
                "LLM tool-trigger decision."
            )
        )