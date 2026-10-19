from dataclasses import dataclass
from datetime import datetime
from brain.tier.models import BrainTier


@dataclass(frozen=True)
class LLMUsageRecord:
    request_id: str
    user_id: str | None


    provider: str
    model: str

    brain_tier: BrainTier | None = None

    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None
    total_tokens: int | None = None

    estimated_cost: float | None = None
    latency: float | None = None

    success: bool = True
    error: str | None = None

    created_at: datetime | None = None