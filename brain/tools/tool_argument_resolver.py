from brain.base.brain_request import BrainRequest

from brain.tools.tool_call import ToolCall
from brain.tools.tool_decision import ToolDecision
from brain.tools.tool_registry import ToolRegistry


class ToolArgumentResolver:

    """
    Resolves arguments for a selected tool.

    Responsibilities:
    - find the selected tool
    - read its schema
    - prepare a ToolCall

    It does NOT:
    - select the tool
    - execute the tool
    - validate arguments
    - handle permissions
    """

    def __init__(
        self,
        registry: ToolRegistry
    ):
        self.registry = registry

    def resolve(
        self,
        request: BrainRequest,
        decision: ToolDecision
    ) -> ToolCall | None:

        # ==========================================
        # NO TOOL
        # ==========================================

        if not decision.requires_tool:
            return None

        # ==========================================
        # MISSING TOOL NAME
        # ==========================================

        if not decision.tool_name:
            return None

        # ==========================================
        # FIND TOOL
        # ==========================================

        tool = self.registry.get(
            decision.tool_name
        )

        if tool is None:
            return None

        # ==========================================
        # READ TOOL SCHEMA
        # ==========================================

        schema = tool.schema

        # ==========================================
        # PREPARE ARGUMENTS
        # ==========================================

        arguments = {}

        if len(schema.parameters) == 1:

            parameter_name = next(
                iter(schema.parameters)
            )

            arguments[parameter_name] = request.query

        # ==========================================
        # CREATE TOOL CALL
        # ==========================================

        return ToolCall(
            tool_name=tool.name,
            arguments=arguments
        )