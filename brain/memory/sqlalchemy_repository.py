

from sqlalchemy.orm import Session


from brain.memory.repository import MemoryRepository
from brain.memory.memory_model import Memory

from brain.embeddings.embedding_service import EmbeddingService
from brain.embeddings.similarity import SimilarityService

from database.models import MemoryEntity


class SQLAlchemyMemoryRepository(MemoryRepository):

    def __init__(self, session: Session):
        self.session = session
        self.embedding_service = EmbeddingService()
        self.similarity_service = SimilarityService()

    # =====================================================
    # INSERT
    # =====================================================

    def insert(self, memory: Memory) -> Memory:

        entity = MemoryEntity(
            memory_id=memory.memory_id,
            user_id=memory.user_id,
            category=memory.category,
            key=memory.key,
            value=str(memory.value),
            embedding=memory.embedding,
            association_embedding=memory.association_embedding,
            confidence=memory.confidence,

        )
        print("\n===== INSERT CHECK =====")
        print("KEY:", memory.key)
        print("Embedding Type:", type(memory.embedding))
        print("Embedding Length:", len(memory.embedding) if memory.embedding else None)
        print("========================")

        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)

        return memory

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, memory: Memory) -> Memory:
        entity = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.memory_id == memory.memory_id,
                MemoryEntity.user_id == memory.user_id,
        )
            .first()
    )

        if entity is None:
            raise ValueError("Memory not found.")

        entity.category = memory.category
        entity.key = memory.key
        entity.value = str(memory.value)
        entity.embedding = memory.embedding
        entity.confidence = memory.confidence
        entity.association_embedding = memory.association_embedding

        self.session.commit()
        self.session.refresh(entity)

        return self._to_domain(entity)

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, memory_id: str):
        raise NotImplementedError

        # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        memory_id: str
    ) -> Memory | None:

        entity = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.memory_id == memory_id
            )
            .first()
        )

        if entity is None:
            return None

        return self._to_domain(entity)

    # =====================================================
    # FIND BY KEY
    # =====================================================

    def find_by_key(
        self,
        user_id: int,
        category: str,
        key: str,
    ):

        entity = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.user_id == user_id,
                MemoryEntity.category == category,
                MemoryEntity.key == key,
            )
            .first()
        )

        if entity is None:
            return None

        return self._to_domain(entity)



        # =====================================================
    # SEMANTIC MEMORY CANDIDATE SEARCH
    # =====================================================

    def search_similar_memory(
        self,
        memory: Memory,
        threshold: float = 0.75
    ):

        if memory.embedding is None:
            return None

        entities = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.user_id == memory.user_id,
                MemoryEntity.category == memory.category,
            )
            .all()
        )

        best_memory = None
        best_score = 0.0

        for entity in entities:

            if entity.embedding is None:
                continue

            score = self.similarity_service.cosine_similarity(
                memory.embedding,
                entity.embedding
            )

            print(
                "SEMANTIC CONFLICT CHECK:",
                memory.key,
                "<->",
                entity.key,
                "| score=",
                round(score, 3)
            )

            if score > best_score:

                best_score = score
                best_memory = entity

        if (
            best_memory is not None
            and best_score >= threshold
        ):

            print(
                "SEMANTIC MATCH:",
                best_memory.key,
                "| score=",
                round(best_score, 3)
            )

            return self._to_domain(best_memory)

        return None







    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(self, user_id: int):

        entities = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.user_id == user_id
            )
            .all()
        )

        return [
            self._to_domain(entity)
            for entity in entities
        ]

    # =====================================================
    # KEYWORD SEARCH
    # =====================================================

    def search_keyword(
        self,
        user_id: int,
        query: str
    ):
        entities = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.user_id == user_id,
                MemoryEntity.key.ilike(f"%{query}%")
            )
            .all()
        )

        return [
            self._to_domain(entity)
            for entity in entities
        ]

    # =====================================================
    # VECTOR SEARCH
    # =====================================================

    def search_vector(
        self,
        user_id: int,
        query: str
    ):

        query_embedding = self.embedding_service.generate(query)



        entities = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.user_id == user_id
            )
            .all()
        )

        scored = []

        for entity in entities:



            if entity.embedding is None:
                continue

            score = self.similarity_service.cosine_similarity(
                query_embedding,
                entity.embedding
            )

            scored.append(
                (
                    score,
                    entity
                )
            )

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
           (self._to_domain(entity), score)
            for score, entity in scored[:5]
        ]

    def search_vector_from_memories(
        self,
        memories: list[Memory],
        query: str
    ) -> list[tuple[Memory, float]]:
        """Rank already-loaded memories by cosine similarity."""
        query_embedding = self.embedding_service.generate(query)
        scored = []

        for memory in memories:
            if memory.embedding is None:
                continue

            score = self.similarity_service.cosine_similarity(
                query_embedding,
                memory.embedding
            )
            scored.append((memory, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:5]

    # =====================================================
    # UPDATE ACCESS
    # =====================================================

    def update_access(self, memory: Memory) -> None:

        entity = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.memory_id == memory.memory_id,
                MemoryEntity.user_id == memory.user_id,
            )
            .first()
        )

        if entity is None:
            return

        entity.access_count = memory.access_count
        entity.last_accessed = memory.last_accessed

        self.session.commit()



            # =====================================================
    # USER-SCOPED MEMORY UPDATE
    # =====================================================

    def update_for_user(
        self,
        memory: Memory
    ) -> Memory:

        entity = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.memory_id == memory.memory_id,
                MemoryEntity.user_id == memory.user_id,
            )
            .first()
        )

        if entity is None:
            raise ValueError("Memory not found.")

        entity.category = memory.category
        entity.key = memory.key
        entity.value = str(memory.value)
        entity.embedding = memory.embedding
        entity.association_embedding = (
            memory.association_embedding
        )
        entity.confidence = memory.confidence

        self.session.commit()
        self.session.refresh(entity)

        return self._to_domain(entity)

    # =====================================================
    # USER-SCOPED MEMORY DELETE
    # =====================================================

    def delete_for_user(
        self,
        memory_id: str,
        user_id: int
    ) -> bool:

        entity = (
            self.session.query(MemoryEntity)
            .filter(
                MemoryEntity.memory_id == memory_id,
                MemoryEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return False

        self.session.delete(entity)
        self.session.commit()

        return True

    # =====================================================
    # DOMAIN CONVERTER
    # =====================================================

    def _to_domain(
        self,
        entity: MemoryEntity
    ) -> Memory:

        return Memory(
            memory_id=entity.memory_id,
            user_id=entity.user_id,
            category=entity.category,
            key=entity.key,
            value=entity.value,
            embedding=entity.embedding,
            association_embedding=entity.association_embedding,
            confidence=entity.confidence,
        )