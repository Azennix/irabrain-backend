from brain.tools.tool_registry import ToolRegistry
from brain.tools.tool_result import ToolResult


class ToolExecutor:

    """
    Executes tools registered in the ToolRegistry.

    It does not decide which tool should be used.
    It only executes the requested tool.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(
        self,
        tool_name: str,
        **kwargs
    ) -> ToolResult:

        tool = self.registry.get(tool_name)

        if tool is None:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}"
            )

        try:
            return tool.execute(**kwargs)

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc)
            )