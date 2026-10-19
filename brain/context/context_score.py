from dataclasses import dataclass

from brain.memory.memory_model import Memory


@dataclass
class ContextScore:

    memory: Memory

    retrieval_score: float
    memory_score: float
    context_score: float