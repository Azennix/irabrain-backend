from dataclasses import dataclass

from brain.tier.capabilities import Capability


@dataclass(frozen=True, slots=True)
class CapabilityRequirement:
    capability: Capability
    confidence: float = 1.0
    required_context_window: int = 0
    complexity: float = 0.0



    def __post_init__(self):
        if not isinstance(self.capability, Capability):
            raise TypeError("capability must be a Capability.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0."
            )

        if self.required_context_window < 0:
            raise ValueError(
                "required_context_window cannot be negative."
            )
        if not 0.0 <= self.complexity <= 1.0:
            raise ValueError(
                "complexity must be between 0.0 and 1.0."
    )