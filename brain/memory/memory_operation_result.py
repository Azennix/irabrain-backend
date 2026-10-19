from dataclasses import dataclass

from brain.memory.memory_operation import MemoryOperation


@dataclass(slots=True)
class MemoryOperationResult:

    operation: MemoryOperation

    confidence: float