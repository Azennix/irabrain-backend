from brain.retrieval.association_builder import AssociationBuilder
from brain.memory.memory_stats import MemoryStats
from brain.memory.memory_category import MemoryCategory
from brain.memory.repository import MemoryRepository
from brain.memory.importance_scorer import MemoryImportanceScorer
from brain.embeddings.embedding_service import EmbeddingService
class MemoryService:

    def __init__(
        self,
        extractor,
        validator,
        resolver,
        writer,
        importance_scorer=None,
        cleaner=None,
        repository=None,


    ):

        self.extractor = extractor
        self.resolver = resolver
        self.writer = writer
        self.importance_scorer = importance_scorer or MemoryImportanceScorer()
        self.validator = validator
        self.cleaner = cleaner
        self.repository = repository
        self.stats = MemoryStats()
        self.embedding_service = EmbeddingService()
        self.association_builder = AssociationBuilder()

    def recall_name(self, user_id: int, category: MemoryCategory, key: str):
        return self.repository.find_by_key(user_id=user_id, category=category.value, key=key)

    def store(self, request):
        result = self.extractor.extract(request)
        print("AFTER EXTRACTOR")
        print(result.memories)
        result = self.validator.validate(result)
        print("AFTER VALIDATOR")
        print(result.memories)

        if self.cleaner:
            result.memories = self.cleaner.clean(result.memories)
        print("AFTER CLEANER")
        print(result.memories)
        print("\n===== IMPORTANCE =====")
        for memory in result.memories:
            print(
        memory.category,
        memory.key,
        memory.value,
        memory.confidence
    )

        print("======================\n")

        for memory in result.memories:
            memory.embedding = self.embedding_service.generate(f"{memory.key}: {memory.value}")

            association_text =  self.association_builder.build(memory)

            memory.association_embedding = (
            self.embedding_service.generate(
             association_text
    )
)
            print(
               "Association embedding:",
                 len(memory.association_embedding)
                if memory.association_embedding
                else None
)

            print("\n===== EMBEDDING =====")
            print(memory.key)
            print(type(memory.embedding))
            try:
                print(len(memory.embedding))
                print(memory.embedding[:5])
            except Exception:
                pass
            print("=====================")

            memory.importance = self.importance_scorer.score(memory)




        print("\n===== BEFORE RESOLVER =====")

        for memory in result.memories:
         print(
        memory.category,
        memory.key,
        memory.value,
        memory.importance
    )

        print("==========================\n")
        plan = self.resolver.resolve(result)

        print("\n===== RESOLUTION PLAN =====")
        print("INSERT:")
        for memory in plan.insert:
            print(memory.key, memory.value)

        print("UPDATE:")
        for memory in plan.update:
            print(memory.key, memory.value)

        print("===========================\n")

        write_result = self.writer.write(plan)
        return write_result



    def get_all_memories(self, user_id: int):
        return self.repository.get_all(user_id)
        # =====================================================
    # EDIT MEMORY
    # =====================================================

    def edit_memory(
        self,
        user_id: int,
        memory_id: str,
        category: str,
        key: str,
        value: str,
    ):
        memory = self.repository.get_by_id(
            memory_id
        )

        if memory is None:
            raise ValueError("Memory not found.")

        if memory.user_id != user_id:
            raise ValueError("Memory not found.")

        memory.category = category
        memory.key = key
        memory.value = value

        # Rebuild the semantic embedding because
        # the actual memory content changed.
        memory.embedding = (
            self.embedding_service.generate(
                f"{memory.key}: {memory.value}"
            )
        )

        # Rebuild the association embedding
        # using the updated memory.
        association_text = (
            self.association_builder.build(
                memory
            )
        )

        memory.association_embedding = (
            self.embedding_service.generate(
                association_text
            )
        )

        return self.repository.update_for_user(
            memory
        )

    # =====================================================
    # FORGET MEMORY
    # =====================================================

    def forget_memory(
        self,
        user_id: int,
        memory_id: str,
    ) -> bool:

        memory = self.repository.get_by_id(
            memory_id
        )

        if memory is None:
            return False

        if memory.user_id != user_id:
            return False

        return self.repository.delete_for_user(
            memory_id=memory_id,
            user_id=user_id,
        )


    def get_stats(self, user_id):
        memories = self.repository.get_all(user_id)
        return self.stats.calculate(memories)


# Example usage removed to avoid NameError: memory_service is not defined
    def get_core_identity(self, user_id: int) -> dict:
     """
    Cheap, always-safe fetch — no embeddings, no ranking, no LLM.
    Just pulls a few always-relevant facts directly from the DB.
    """
     memories = self.repository.get_all(user_id)

     print("\n===== ALL MEMORIES FOR CORE IDENTITY =====")

     for memory in memories:
      print(
        "category =", repr(memory.category),
        "| key =", repr(memory.key),
        "| value =", repr(memory.value)
    )

      print("==========================================")

     core = {}
     for memory in memories:
        if memory.category in (MemoryCategory.IDENTITY.value,
                        MemoryCategory.GOAL.value):
            core.setdefault(memory.category, {})[memory.key] = memory.value

     return core