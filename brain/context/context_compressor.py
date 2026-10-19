class ContextCompressor:

    def compress(self, scores):

        if not scores:
            return {}

        context = {}

        print("\n===== COMPRESSED CONTEXT =====")

        for score in scores:

            memory = score.memory

            category = memory.category

            if category not in context:
                context[category] = {}

            context[category][memory.key] = memory.value

            print(
                f"{memory.key} = {memory.value}"
            )

        print("==============================\n")

        return context