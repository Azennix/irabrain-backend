from dataclasses import dataclass


@dataclass(frozen=True)
class ContextConfig:

    max_memories: int = 8

    min_retrieval_score: float = 0.05

    retrieval_weight: float = 0.70
    memory_weight: float = 0.30
    min_context_score: float = 0.15
    min_association_score: float = 0.25