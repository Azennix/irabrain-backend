from brain.llm.usage import LLMUsageRecord
from brain.self_development.domain.enums import (
    SignalSeverity,
    SignalType,
)
from brain.self_development.domain.models import DevelopmentSignal
from brain.self_development.observation.signal_collector import (
    SignalCollector,
)


class LLMTelemetrySignalEvaluator:
    """
    Converts meaningful LLM telemetry events into
    existing Self-Development DevelopmentSignals.

    This component does not:
    - decide improvements
    - investigate root causes
    - modify code
    - execute development
    """

    def __init__(
        self,
        signal_collector: SignalCollector | None = None,
    ):
        self.signal_collector = (
            signal_collector
            or SignalCollector()
        )

    def evaluate(
        self,
        usage: LLMUsageRecord,
    ) -> DevelopmentSignal | None:

        if usage is None:
            raise ValueError(
                "LLM usage record cannot be None."
            )

        # -------------------------------------------------
        # FAILURE SIGNAL
        # -------------------------------------------------

        if not usage.success:

            return self.signal_collector.collect(
                signal_type=SignalType.FAILURE,
                severity=SignalSeverity.MEDIUM,
                source="llm_usage",
                description=(
                    "An LLM request failed during execution."
                ),
                evidence={
                    "request_id": usage.request_id,
                    "user_id": usage.user_id,
                    "provider": usage.provider,
                    "model": usage.model,
                    "latency": usage.latency,
                    "error": usage.error,
                    "created_at": (
                        usage.created_at.isoformat()
                        if usage.created_at
                        else None
                    ),
                },
            )

        # -------------------------------------------------
        # PERFORMANCE SIGNAL
        # -------------------------------------------------

        if (
            usage.latency is not None
            and usage.latency >= 10.0
        ):

            return self.signal_collector.collect(
                signal_type=SignalType.PERFORMANCE,
                severity=SignalSeverity.MEDIUM,
                source="llm_usage",
                description=(
                    "An LLM request exceeded the "
                    "latency threshold."
                ),
                evidence={
                    "request_id": usage.request_id,
                    "user_id": usage.user_id,
                    "provider": usage.provider,
                    "model": usage.model,
                    "latency": usage.latency,
                    "latency_threshold": 10.0,
                    "created_at": (
                        usage.created_at.isoformat()
                        if usage.created_at
                        else None
                    ),
                },
            )

        return None