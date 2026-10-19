from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IntentType(str, Enum):

    CONVERSATION = "conversation"
    INFORMATION = "information"
    MEMORY = "memory"
    MEMORY_MANAGEMENT = "memory_management"
    COMPARISON = "comparison"
    DECISION = "decision"
    TASK = "task"
    TOOL = "tool"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:

    intent: IntentType

    confidence: float = 0.0

    entities: dict[str, Any] = field(
        default_factory=dict
    )

    requires_reasoning: bool = False

    requires_memory: bool = False

    requires_tool: bool = False