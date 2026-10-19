from brain.llm.usage import LLMUsageRecord
from brain.llm.llm_usage_model import LLMUsage


class LLMUsagePersistence:
    """
    Persists normalized LLM usage records.

    Responsibilities:
    - convert LLMUsageRecord into SQLAlchemy model data
    - persist usage telemetry to PostgreSQL

    It does NOT:
    - know about LLM providers
    - calculate provider-specific usage
    - trigger Self-Development
    - modify LLM responses
    """

    def __init__(self, session):
        self.session = session

    def save(
        self,
        usage: LLMUsageRecord,
    ) -> None:

        record = LLMUsage(
            request_id=usage.request_id,
            user_id=usage.user_id,
            provider=usage.provider,
            model=usage.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cached_tokens=usage.cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost=usage.estimated_cost,
            latency=usage.latency,
            success=usage.success,
            error=usage.error,
            created_at=usage.created_at,
        )

        self.session.add(record)
        self.session.commit()