from dataclasses import dataclass

from brain.memory.memory_model import Memory


@dataclass
class RetrievalResult:

    memory: Memory

    keyword_score: float = 0.0

    semantic_score: float = 0.0

    association_score: float = 0.0

    concept_score: float = 0.0

    final_score: float = 0.0