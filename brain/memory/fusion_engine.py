class FusionEngine:

    def fuse(
        self,
        keyword_results,
        semantic_results
    ):

        merged = {}

        for memory in keyword_results:
            merged[memory.memory_id] = memory

        for memory in semantic_results:
            merged[memory.memory_id] = memory

        return list(merged.values())