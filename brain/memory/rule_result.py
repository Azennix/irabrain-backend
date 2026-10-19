from dataclasses import dataclass, field

from brain.memory.memory_model import Memory


@dataclass(slots=True)
class RuleResult:

    matched: bool

    memories: list[Memory] = field(default_factory=list)

    confidence: float = 0.0