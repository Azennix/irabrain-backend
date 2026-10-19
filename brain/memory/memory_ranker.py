from brain.memory.memory_model import Memory


class MemoryRanker:

    def rank(
        self,
        memories: list[Memory]
    ) -> list[Memory]:

        return sorted(

            memories,

            key=lambda memory: (

                memory.importance,

                memory.confidence

            ),

            reverse=True

        )