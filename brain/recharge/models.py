from dataclasses import dataclass, field
from typing import Any
from decimal import Decimal
from brain.tier.models import BrainTier

@dataclass(frozen=True, slots=True)
class BrainUsageContext:
    """
    Normalized context used by the Brain Unit calculation system.

    This is intentionally independent from any payment provider,
    wallet implementation, or specific LLM provider.
    """

    request_id: str
    user_id: int | None = None
    brain_tier: BrainTier | None = None

    capability: str | None = None
    task_type: str | None = None

    provider: str | None = None
    model: str | None = None

    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None
    total_tokens: int | None = None

    estimated_cost: float | None = None

    tool_usage: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BrainUnitResult:
    """
    Result produced by a Brain Unit calculation policy.

    `units` is the normalized product consumption.
    """

    units: Decimal

    calculation_version: str

    basis: str

    metadata: dict[str, Any] = field(default_factory=dict)