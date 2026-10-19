from collections import Counter
class MemoryStats:

    def calculate(self, memories):

        category_counts = Counter(
            memory.category
            for memory in memories
        )

        stats = {
            "total": len(memories),
            **category_counts
        }

        return stats