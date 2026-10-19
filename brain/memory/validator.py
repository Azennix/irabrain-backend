from brain.memory.memory_extraction_result import MemoryExtractionResult


class MemoryValidator:

   INVALID_VALUES = {
    "",
    " ",
    "this",
    "that",
    "it",
    "they",
    "them",
    "these",
    "those",
    "something",
    "anything",
    "everything",
    "someone",
    "somebody",
    "unknown",
    "none",
    "null",
    "n/a"
}

   def validate(
        self,
        result: MemoryExtractionResult
    ) -> MemoryExtractionResult:

        valid_memories = []

        for memory in result.memories:

            # Empty key
            if not memory.key:
                continue

            # Empty value
            if not str(memory.value).strip():
                continue

            # Invalid value
            if str(memory.value).lower() in self.INVALID_VALUES:
                continue

            # Low confidence
            if memory.confidence < 0.70:
                continue

            valid_memories.append(memory)

        result.memories = valid_memories

        return result