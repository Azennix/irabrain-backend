from brain.llm.usage import LLMUsageRecord
from brain.llm.usage_persistence import LLMUsagePersistence
from brain.llm.llm_telemetry_signal_evaluator import (
    LLMTelemetrySignalEvaluator,
)
from brain.self_development.observation.observation_coordinator import (
    ObservationCoordinator,
)


class LLMUsageRecordHandler:
    """
    Coordinates the destinations for normalized LLM telemetry.

    It keeps UsageTracker provider-agnostic while allowing
    telemetry persistence and Self-Development observation
    to receive the same usage record.
    """

    def __init__(
        self,
        persistence: LLMUsagePersistence,
        telemetry_evaluator: LLMTelemetrySignalEvaluator,
        observation_coordinator: ObservationCoordinator,
        brain_usage_adapter=None,
    ):

        if persistence is None:
            raise ValueError("Persistence is required.")

        if telemetry_evaluator is None:
            raise ValueError("Telemetry evaluator is required.")

        if observation_coordinator is None:
            raise ValueError("Observation coordinator is required.")



        self.persistence = persistence
        self.telemetry_evaluator = telemetry_evaluator
        self.observation_coordinator = observation_coordinator
        self.brain_usage_adapter = brain_usage_adapter

    def handle(
        self,
        usage: LLMUsageRecord,
    ) -> None:

        if usage is None:
            raise ValueError(
                "LLM usage record cannot be None."
            )

        # Always persist normalized telemetry.
        self.persistence.save(usage)

        # Evaluate telemetry for meaningful
        # Self-Development observation.
        signal = self.telemetry_evaluator.evaluate(
            usage
        )

        # Forward meaningful signals into the existing
        # Self-Development observation boundary.
        if signal is not None:
            self.observation_coordinator.process(
                [signal]
            )

        if (
            self.brain_usage_adapter is not None
            and usage.success
            and usage.user_id is not None
            and usage.estimated_cost is not None
    ):
            self.brain_usage_adapter.settle(usage)