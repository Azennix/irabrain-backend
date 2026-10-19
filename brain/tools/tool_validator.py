from brain.tools.tool_decision import ToolDecision
from brain.tools.tool_registry import ToolRegistry


class ToolValidator:

    """
    Validates a ToolDecision before execution.

    It does NOT:
    - execute the tool
    - select another tool
    - handle permissions
    - modify tool arguments

    It only verifies that the selected tool
    exists in the registry.
    """

    def __init__(
        self,
        registry: ToolRegistry
    ):
        self.registry = registry

    def validate(
        self,
        decision: ToolDecision
    ) -> bool:

        # ==========================================
        # NO TOOL REQUIRED
        # ==========================================

        if not decision.requires_tool:
            return True

        # ==========================================
        # TOOL NAME MISSING
        # ==========================================

        if not decision.tool_name:
            return False

        # ==========================================
        # TOOL NOT REGISTERED
        # ==========================================

        tool = self.registry.get(
            decision.tool_name
        )

        if tool is None:
            return False

        # ==========================================
        # VALID
        # ==========================================

        return True