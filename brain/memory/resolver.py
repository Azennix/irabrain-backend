from brain.memory.memory_extraction_result import MemoryExtractionResult
from brain.memory.repository import MemoryRepository
from brain.memory.conflict_resolver import MemoryConflictResolver
from brain.memory.resolution_plan import ResolutionPlan
from brain.memory.merger import MemoryMerger
from brain.llm.llm_service import LLMService


class MemoryResolver:

    def __init__(
        self,
        repository: MemoryRepository,
        llm_service: LLMService
    ):
        self.repository = repository

        self.merger = MemoryMerger()

        self.conflict_resolver = MemoryConflictResolver(
            llm_service
        )

    def resolve(
        self,
        result: MemoryExtractionResult
    ) -> ResolutionPlan:

        if not result.memories:
            return ResolutionPlan()

        plan = ResolutionPlan()

        for memory in result.memories:

            print("\n========== RESOLVER ==========")

            print(
                "Incoming:",
                memory.category,
                "|",
                memory.key,
                "=",
                memory.value
            )

            # =================================================
            # 1. EXACT KEY SEARCH
            # =================================================

            existing = self.repository.find_by_key(
                user_id=memory.user_id,
                category=memory.category,
                key=memory.key
            )

            print("\n===== EXACT KEY LOOKUP =====")
            print("USER ID :", memory.user_id)
            print("CATEGORY:", repr(memory.category))
            print("KEY     :", repr(memory.key))
            print("FOUND   :", existing)

            # =================================================
            # 2. EXACT MATCH
            # =================================================

            if existing is not None:

                print(
                    "EXACT KEY MATCH:",
                    existing.key,
                    "=",
                    existing.value
                )

            # =================================================
            # 3. NO EXACT MATCH -> SEMANTIC SEARCH
            # =================================================

            else:

                print(
                    "NO EXACT KEY MATCH -> SEMANTIC SEARCH"
                )

                existing = (
                    self.repository.search_similar_memory(
                        memory
                    )
                )

            print(
                "SEMANTIC/EXACT EXISTING:",
                existing
            )

            # =================================================
            # 4. NO EXISTING MEMORY
            # =================================================

            if existing is None:

                print("ACTION -> INSERT")

                plan.insert.append(memory)

                continue

            # =================================================
            # 5. EXISTING MEMORY
            # =================================================

            print(
                "Existing value:",
                existing.value
            )

            # =================================================
            # 6. AI CONFLICT RESOLUTION
            # =================================================

            decision = self.conflict_resolver.resolve(
                existing=existing,
                incoming=memory
            )

            action = decision["action"]
            final_value = decision["final_value"]

            print(
                "AI ACTION:",
                action
            )

            print(
                "AI FINAL VALUE:",
                final_value
            )

            # =================================================
            # 7. REPLACE
            # =================================================

            if action == "replace":

                print("ACTION -> AI REPLACE")

                existing.value = final_value
                existing.confidence = memory.confidence
                existing.embedding = memory.embedding
                existing.importance = memory.importance
                existing.updated_at = memory.updated_at

                plan.update.append(existing)

            # =================================================
            # 8. MERGE
            # =================================================

            elif action == "merge":

                print("ACTION -> AI MERGE")

                existing.value = final_value
                existing.confidence = memory.confidence
                existing.embedding = memory.embedding
                existing.importance = memory.importance
                existing.updated_at = memory.updated_at

                plan.merge.append(existing)
                plan.update.append(existing)

            # =================================================
            # 9. IGNORE
            # =================================================

            elif action == "ignore":

                print("ACTION -> AI IGNORE")

                plan.ignore.append(memory)

            else:

                print(
                    "WARNING: UNKNOWN ACTION:",
                    action
                )

        # =====================================================
        # DEBUG
        # =====================================================

        print(
            "\n========== RESOLUTION PLAN =========="
        )

        print("INSERT:", len(plan.insert))
        print("UPDATE:", len(plan.update))
        print("MERGE :", len(plan.merge))
        print("IGNORE:", len(plan.ignore))

        print(
            "====================================="
        )

        return plan