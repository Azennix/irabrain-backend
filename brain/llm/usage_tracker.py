from typing import Callable, Optional

from brain.llm.usage import LLMUsageRecord
from datetime import datetime, timezone
class UsageTracker:
    """
    Collects normalized LLM usage records.

    Responsibilities:
    - receive usage telemetry
    - validate the record
    - forward the record to an optional persistence handler

    It does NOT:
    - know about Ollama/OpenAI/etc.
    - calculate provider-specific usage
    - modify LLM responses
    - trigger Self-Development
    """

    def __init__(
        self,
        record_handler: Optional[
            Callable[[LLMUsageRecord], None]
        ] = None,
    ):
        self.record_handler = record_handler

    def record(
        self,
        usage: LLMUsageRecord,
    ) -> None:

        if usage is None:
            raise ValueError(
                "LLM usage record cannot be None."
            )

        if not usage.request_id:
            raise ValueError(
                "LLM usage request_id cannot be empty."
            )

        if not usage.provider:
            raise ValueError(
                "LLM usage provider cannot be empty."
            )

        if not usage.model:
            raise ValueError(
                "LLM usage model cannot be empty."
            )
        if usage.created_at is None:
            usage = LLMUsageRecord(
                request_id=usage.request_id,
                user_id=usage.user_id,
                provider=usage.provider,
                model=usage.model,
                brain_tier=usage.brain_tier,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cached_tokens=usage.cached_tokens,
                reasoning_tokens=usage.reasoning_tokens,
                total_tokens=usage.total_tokens,
                estimated_cost=usage.estimated_cost,
                latency=usage.latency,
                success=usage.success,
                error=usage.error,
                created_at=datetime.now(timezone.utc),
          )

        if self.record_handler is not None:
            self.record_handler(usage)