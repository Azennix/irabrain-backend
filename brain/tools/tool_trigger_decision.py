from dataclasses import dataclass


@dataclass(slots=True)
class ToolTriggerDecision:
    """
    Represents the decision about whether the current
    request should trigger the tool system.

    This class does not select or execute a tool.
    It only represents the trigger decision.
    """

    should_use_tools: bool

    confidence: float = 0.0

    reason: str | None = None