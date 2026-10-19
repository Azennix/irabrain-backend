from dataclasses import dataclass, field

from brain.reasoning.evidence import Evidence
from brain.reasoning.alternative import Alternative
from brain.reasoning.strategies import ReasoningStrategy
from brain.reasoning.reasoning_item import ReasoningItem

@dataclass(slots=True)
class ReasoningResult:

    strategy: ReasoningStrategy

    conclusion: str

    confidence: float

    evidence: list[Evidence] = field(
        default_factory=list
    )

    alternatives: list[ReasoningItem] = field(
        default_factory=list
    )

    risks: list[ReasoningItem] = field(
        default_factory=list
    )

    assumptions: list[ReasoningItem] = field(
        default_factory=list
    )