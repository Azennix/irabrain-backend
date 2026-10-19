from dataclasses import dataclass


@dataclass(slots=True)
class ToolExecutionPolicy:
    """
    Defines the execution policy for a tool operation.

    This class does not execute the tool.
    It only describes whether execution is allowed
    and whether user confirmation is required.
    """

    allowed: bool = True

    requires_confirmation: bool = False

    risk_level: str = "low"

    reason: str | None = None