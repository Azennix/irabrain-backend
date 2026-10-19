from dataclasses import dataclass, field

from brain.memory.memory_action import MemoryAction
from brain.memory.memory_model import Memory


@dataclass(slots=True)
class MemoryResult:
    """
    Standard response returned by the Memory Engine.
    """

    action: MemoryAction

    success: bool = True

    stored: list[Memory] = field(default_factory=list)

    updated: list[Memory] = field(default_factory=list)

    retrieved: list[Memory] = field(default_factory=list)

    message: str = ""