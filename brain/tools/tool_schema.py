from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ToolSchema:

    """
    Describes the input contract required by a tool.
    """

    name: str

    description: str

    parameters: dict[str, Any]