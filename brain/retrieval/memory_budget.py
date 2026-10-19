class MemoryBudget:

    def __init__(
        self,
        max_memories: int = 10
    ):
        self.max_memories = max_memories

    def apply(
        self,
        memories
    ):

        return memories[: self.max_memories]