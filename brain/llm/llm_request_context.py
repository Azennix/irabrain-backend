from dataclasses import dataclass

from brain.tier.models import BrainTier


@dataclass(frozen=True)
class LLMRequestContext:
    """
    Request-scoped context used by LLM infrastructure.

    This carries request identity and Brain Tier information.
    It does not contain provider-specific data.
    """

    request_id: str
    user_id: int | None = None
    brain_tier: BrainTier | None = None