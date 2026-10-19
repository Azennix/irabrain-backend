from dataclasses import dataclass

from brain.reasoning.evidence import EvidenceSource


@dataclass(frozen=True, slots=True)
class ReasoningItem:

    content: str

    source: EvidenceSource

    confidence: float = 1.0

    reference_id: str | None = None