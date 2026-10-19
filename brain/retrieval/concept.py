from dataclasses import dataclass

@dataclass
class Concept:

    text: str
    embedding: list[float] | None = None
    confidence: float = 1.0