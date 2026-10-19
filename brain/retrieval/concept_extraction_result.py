from dataclasses import dataclass, field

from brain.retrieval.concept import Concept


@dataclass
class ConceptExtractionResult:

    concepts: list[Concept] = field(default_factory=list)

    confidence: float = 0.0

    reasoning: str = ""