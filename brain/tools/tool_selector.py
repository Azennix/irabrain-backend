from brain.base.brain_request import BrainRequest
from brain.llm.memory_llm_service import MemoryLLMService
from brain.tools.tool_decision import ToolDecision
from brain.tools.tool_registry import ToolRegistry


class ToolSelector:

    """
    Selects the most appropriate registered tool
    for a request.

    It does NOT:
    - execute the tool
    - validate the tool
    - handle permissions

    It only selects a tool.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        llm_service: MemoryLLMService
    ):
        self.registry = registry

        if llm_service is None:
            raise ValueError(
                "ToolSelector requires an LLM provider."
            )
        self.llm_service = llm_service

    def select(
        self,
        request: BrainRequest
    ) -> ToolDecision:

        tools = self.registry.list_tools()

        if not tools:

            return ToolDecision(
                requires_tool=False,
                tool_name=None,
                confidence=0.0
            )

        tool_descriptions = []

        for name in tools:

            tool = self.registry.get(name)

            if tool:

                tool_descriptions.append(
                    f"{tool.name}: {tool.description}"
                )

        prompt = f"""
Choose the most appropriate tool for the user's request.

Return ONLY valid JSON.

Required format:

{{
    "requires_tool": true,
    "tool_name": "tool_name",
    "confidence": 0.0
}}

Rules:

- Select ONLY from the available tools.
- Do not invent a tool.
- Set requires_tool=false if none of the available
  tools are appropriate.
- Do not execute the tool.
- Do not perform the requested task.
- Only decide which tool should handle it.

Available tools:

{chr(10).join(tool_descriptions)}

User request:

{request.query}
"""

        result = self.llm_service.generate_structured(
            prompt=prompt,
            temperature=0.0
        )

        tool_name = result.get("tool_name")

        if (
            not result.get("requires_tool", False)
            or tool_name not in tools
        ):

            return ToolDecision(
                requires_tool=False,
                tool_name=None,
                confidence=float(
                    result.get("confidence", 0.5)
                )
            )

        return ToolDecision(
            requires_tool=True,
            tool_name=tool_name,
            confidence=float(
                result.get("confidence", 0.5)
            )
        )