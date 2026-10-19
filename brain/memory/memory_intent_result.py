from dataclasses import dataclass

from brain.memory.memory_intent import MemoryIntent


@dataclass(slots=True)
class MemoryIntentResult:

    intent: MemoryIntent

    confidence: float