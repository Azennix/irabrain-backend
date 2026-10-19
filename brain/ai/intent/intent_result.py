from dataclasses import dataclass


@dataclass(slots=True)
class IntentResult:

    intent: str

    confidence: float