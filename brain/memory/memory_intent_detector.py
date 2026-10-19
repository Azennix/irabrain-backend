from brain.base.brain_request import BrainRequest
from brain.memory.memory_intent import MemoryIntent
from brain.memory.memory_intent_result import MemoryIntentResult
from brain.memory.memory_operation import MemoryOperation
from brain.memory.memory_operation_result import MemoryOperationResult

class MemoryIntentDetector:

    """
    Decides WHAT the user wants to do with memory.

    It DOES NOT extract memory.
    """


def detect(
    self,
    request: BrainRequest
) -> MemoryOperationResult:

    text = request.query.lower().strip()

    if text.endswith("?"):

        return MemoryOperationResult(

            operation=MemoryOperation.RECALL,

            confidence=0.95

        )

    return MemoryOperationResult(

        operation=MemoryOperation.STORE,

        confidence=0.95

    )