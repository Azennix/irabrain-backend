from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ToolCall:

    """
    Represents an executable request for a tool.

    It contains:
    - the selected tool
    - the arguments required by that tool

    It does NOT execute the tool.
    """

    tool_name: str

    arguments: dict[str, Any]