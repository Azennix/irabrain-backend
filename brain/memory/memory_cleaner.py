class MemoryCleaner:

    def clean(self, memories):

        unique = {}

        for memory in memories:

            key = (
                memory.category,
                memory.key
            )

            unique[key] = memory

        return list(unique.values())