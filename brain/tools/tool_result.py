from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ToolResult:

    success: bool

    output: Any = None

    error: str | None = None