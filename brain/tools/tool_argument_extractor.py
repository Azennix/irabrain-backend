from brain.base.brain_request import BrainRequest
from brain.llm.memory_llm_service import MemoryLLMService

from brain.tools.tool_call import ToolCall
from brain.tools.tool_decision import ToolDecision
from brain.tools.tool_registry import ToolRegistry


class ToolArgumentExtractor:

    """
    Extracts structured arguments for a selected tool.

    It does NOT:
    - select the tool
    - execute the tool
    - validate arguments
    - handle permissions

    It converts natural-language requests into
    arguments that match the selected tool schema.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        llm_service: MemoryLLMService | None = None
    ):
        self.registry = registry

        self.llm_service = (
            llm_service
            or MemoryLLMService()
        )

    def extract(
        self,
        request: BrainRequest,
        decision: ToolDecision
    ) -> ToolCall | None:

        if not decision.requires_tool:
            return None

        if not decision.tool_name:
            return None

        tool = self.registry.get(
            decision.tool_name
        )

        if tool is None:
            return None

        schema = tool.schema

        prompt = f"""
Extract the arguments required by the selected tool.

Return ONLY valid JSON.

Tool:
{tool.name}

Description:
{tool.description}

Parameters:
{schema.parameters}

User request:
{request.query}

Rules:
- Return only parameters defined in the tool schema.
- Do not invent parameters.
- Do not execute the tool.
- Extract only the required argument values.
"""

        result = self.llm_service.generate_structured(
            prompt=prompt,
            temperature=0.0
        )

        arguments = {}

        for parameter_name in schema.parameters:

            if parameter_name in result:

                arguments[parameter_name] = (
                    result[parameter_name]
                )

        return ToolCall(
            tool_name=tool.name,
            arguments=arguments
        )