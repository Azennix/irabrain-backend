from dataclasses import dataclass


@dataclass(slots=True)
class ToolDecision:
    """
    Represents the decision about whether a tool should be used.

    This object contains a decision only.
    It does not execute any tool.
    """

    requires_tool: bool

    tool_name: str | None = None

    confidence: float = 0.0

    reason: str | None = None