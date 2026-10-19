from dataclasses import dataclass

from brain.tier.capabilities import Capability


@dataclass(frozen=True, slots=True)
class ModelDefinition:
    model_id: str
    provider: str
    capabilities: frozenset[Capability]
    context_window: int = 0
    cost_per_unit: float = 0.0
    latency_score: float = 0.0
    available: bool = True
    reasoning_strength: float = 0.0

    def __post_init__(self):
        if not self.model_id.strip():
            raise ValueError("model_id cannot be empty.")

        if not self.provider.strip():
            raise ValueError("provider cannot be empty.")

        if self.context_window < 0:
            raise ValueError("context_window cannot be negative.")

        if self.cost_per_unit < 0:
            raise ValueError("cost_per_unit cannot be negative.")

        if self.latency_score < 0:
            raise ValueError("latency_score cannot be negative.")

        if not 0.0 <= self.reasoning_strength <= 1.0:
            raise ValueError(
            "reasoning_strength must be between 0.0 and 1.0."
    )

        if not isinstance(self.capabilities, frozenset):
            raise TypeError("capabilities must be a frozenset.")
