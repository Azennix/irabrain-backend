from dataclasses import dataclass, field

from brain.memory.memory_model import Memory


@dataclass(slots=True)
class MemoryExtractionResult:

    memories: list[Memory] = field(default_factory=list)

    reasoning: str = ""

    confidence: float = 0.0