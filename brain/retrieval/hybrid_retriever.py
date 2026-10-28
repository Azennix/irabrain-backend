from brain.memory.repository import MemoryRepository
from brain.llm.memory_llm_service import MemoryLLMService
from brain.retrieval.duplicate_filter import DuplicateFilter
from brain.retrieval.hybrid_ranker import HybridRanker
from brain.retrieval.retrieval_result import RetrievalResult
from brain.retrieval.concept_extractor import ConceptExtractor
from brain.retrieval.concept_matcher import ConceptMatcher
from brain.retrieval.association_manager import AssociationManager
from brain.retrieval.association_searcher import AssociationSearcher
from brain.retrieval.memory_context_selector import MemoryContextSelector
from brain.retrieval.ranking_config import RankingConfig
import time
class HybridRetriever:


 def __init__(
    self,
    repository: MemoryRepository,
    llm_service: MemoryLLMService
):
    self.repository = repository
    if llm_service is None:
        raise ValueError(
            "HybridRetriever requires an LLM provider."
        )

    self.duplicate_filter = DuplicateFilter()


    self.association_manager = AssociationManager()
    self.association_searcher = AssociationSearcher()

    self.concept_extractor = ConceptExtractor(
        llm_service=llm_service
)

    self.concept_matcher = ConceptMatcher()
    self.context_selector = MemoryContextSelector()
    self.ranker = HybridRanker(
    RankingConfig()
)

 def retrieve(
    self,
    user_id: int,
    query: str
):

    _retrieval_started = time.perf_counter()

    # =====================================================
    # KEYWORD SEARCH
    # =====================================================

    all_memories = self.repository.get_all(user_id)

    if not all_memories:
        print("\n[INFO] No memories found — retrieval skipped")
        return []

    keyword = self.repository.search_keyword(
        user_id,
        query
)

    vector_search_from_memories = getattr(
        self.repository,
        "search_vector_from_memories",
        None
    )

    if callable(vector_search_from_memories):
        vector_results = vector_search_from_memories(
            all_memories,
            query
        )
    else:
        vector_results = self.repository.search_vector(
            user_id,
            query
        )

    vector_memories = [
        memory
        for memory, similarity in vector_results
]

    # =====================================================
    # GENERAL CONTEXT
    # =====================================================

    general_context = (
        self.context_selector.select_general_context(
            all_memories
        )
    )

    print("\n===== GENERAL CONTEXT =====")

    for memory in general_context:
        print(
            memory.key,
            "=",
            memory.value
        )

    # =====================================================
    # ASSOCIATION SEARCH
    # =====================================================

    memory_associations = (
        self.association_manager.build_for_memories(
            all_memories
        )
    )

    association_matches = (
        self.association_searcher.search(
            query,
            memory_associations
        )
    )

    print("\n===== ASSOCIATION MATCHES =====")
    print(association_matches)
    print("===============================\n")

    association_scores = dict(
        association_matches
    )

    print("\n===== ASSOCIATION SCORES =====")

    for memory_id, score in association_scores.items():
     print(
        memory_id,
        "->",
        round(float(score), 3)
    )

     print("==============================\n")

    # =====================================================
    # CREATE RESULTS
    # =====================================================

    results = []

    # -----------------------------------------------------
    # KEYWORD
    # -----------------------------------------------------

    for memory in keyword:

        results.append(
            RetrievalResult(
                memory=memory,
                keyword_score=1.0,
                semantic_score=0.0
            )
        )

    # -----------------------------------------------------
    # VECTOR / SEMANTIC
    # -----------------------------------------------------

    for memory, similarity in vector_results:

        results.append(
            RetrievalResult(
                memory=memory,
                keyword_score=0.0,
                semantic_score=similarity
            )
        )

    # -----------------------------------------------------
    # ASSOCIATION
    # -----------------------------------------------------

    for memory in all_memories:

        if memory.memory_id not in association_scores:
            continue

        similarity = association_scores[
            memory.memory_id
        ]

        results.append(
            RetrievalResult(
                memory=memory,
                association_score=similarity
            )
        )
        print("\n===== ASSOCIATION RESULTS =====")

        for result in results:
         if result.association_score > 0:
           print(
             result.memory.key,
            "=",
            result.memory.value,
            "| association=",
            round(float(result.association_score), 3)
        )

        print("===============================\n")
    # =====================================================
    # CONCEPT SEARCH
    # =====================================================

    concepts = self.concept_extractor.extract(
        query
    )

    # ConceptMatcher expects Memory objects,
    # not (Memory, similarity) tuples.

    matched = self.concept_matcher.match(
        concepts,
        keyword + vector_memories
    )

    print("\n===== MATCHED =====")

    for concept, memory, similarity in matched:

        print(
            concept.text,
            "->",
            memory.key,
            "| similarity=",
            round(similarity, 3)
        )

        results.append(
            RetrievalResult(
                memory=memory,
                concept_score=similarity
            )
        )

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================
    print("\n===== BEFORE DUPLICATE FILTER =====")

    for result in results:
     print(
        result.memory.key,
        "| semantic=", round(result.semantic_score, 3),
        "| association=", round(result.association_score, 3),
        "| keyword=", round(result.keyword_score, 3),
        "| concept=", round(result.concept_score, 3)
    )

    print("====================================")
    results = self.duplicate_filter.filter(
        results
    )
    print("\n===== AFTER DUPLICATE FILTER =====")

    for result in results:
     print(
        result.memory.key,
        "| semantic=", round(result.semantic_score, 3),
        "| association=", round(result.association_score, 3),
        "| keyword=", round(result.keyword_score, 3),
        "| concept=", round(result.concept_score, 3)
    )

     print("===================================")

    # =====================================================
    # FINAL RANK
    # =====================================================

    results = self.ranker.rank(
        results
    )

    print("\n===== FINAL RETRIEVER =====")

    for result in results:

        print(
            result.memory.key,
            "=",
            result.memory.value,
            "| final=",
            round(result.final_score, 3),
            "| semantic=",
            round(result.semantic_score, 3),
            "| keyword=",
            round(result.keyword_score, 3),
            "| association=",
            round(result.association_score, 3),
            "| concept=",
            round(result.concept_score, 3)
        )
    for result in results:
        result.memory.retrieval_score = result.final_score
    print(
        f"RETRIEVAL_TOTAL_MS: "
        f"{(time.perf_counter() - _retrieval_started) * 1000:.2f}"
    )
    return [
        result.memory
        for result in results
    ]
