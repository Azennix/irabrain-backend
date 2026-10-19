from unittest.mock import Mock

from brain.llm.usage import LLMUsageRecord
from brain.llm.usage_record_handler import (
    LLMUsageRecordHandler,
)


def test_handler_persists_and_processes_telemetry():
    persistence = Mock()
    telemetry_evaluator = Mock()
    observation_coordinator = Mock()

    telemetry_evaluator.evaluate.return_value = None

    handler = LLMUsageRecordHandler(
        persistence=persistence,
        telemetry_evaluator=telemetry_evaluator,
        observation_coordinator=observation_coordinator,
    )

    usage = LLMUsageRecord(
        request_id="handler-test-001",
        user_id="1001",
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
        estimated_cost=0.05,
        latency=1.0,
        success=True,
    )

    handler.handle(usage)

    persistence.save.assert_called_once_with(usage)
    telemetry_evaluator.evaluate.assert_called_once_with(usage)
    observation_coordinator.process.assert_not_called()


def test_handler_forwards_meaningful_signal():
    persistence = Mock()
    telemetry_evaluator = Mock()
    observation_coordinator = Mock()

    signal = Mock()
    telemetry_evaluator.evaluate.return_value = signal

    handler = LLMUsageRecordHandler(
        persistence=persistence,
        telemetry_evaluator=telemetry_evaluator,
        observation_coordinator=observation_coordinator,
    )

    usage = LLMUsageRecord(
        request_id="handler-test-002",
        user_id="1002",
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
        estimated_cost=0.05,
        latency=1.0,
        success=True,
    )

    handler.handle(usage)

    persistence.save.assert_called_once_with(usage)
    telemetry_evaluator.evaluate.assert_called_once_with(usage)
    observation_coordinator.process.assert_called_once_with(
        [signal]
    )


def test_handler_settles_successful_usage_when_adapter_exists():
    persistence = Mock()
    telemetry_evaluator = Mock()
    observation_coordinator = Mock()
    brain_usage_adapter = Mock()

    telemetry_evaluator.evaluate.return_value = None

    handler = LLMUsageRecordHandler(
        persistence=persistence,
        telemetry_evaluator=telemetry_evaluator,
        observation_coordinator=observation_coordinator,
        brain_usage_adapter=brain_usage_adapter,
    )

    usage = LLMUsageRecord(
        request_id="handler-test-003",
        user_id="1003",
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
        estimated_cost=0.05,
        latency=1.0,
        success=True,
    )

    handler.handle(usage)

    brain_usage_adapter.settle.assert_called_once_with(usage)


def test_handler_does_not_settle_failed_usage():
    persistence = Mock()
    telemetry_evaluator = Mock()
    observation_coordinator = Mock()
    brain_usage_adapter = Mock()

    telemetry_evaluator.evaluate.return_value = None

    handler = LLMUsageRecordHandler(
        persistence=persistence,
        telemetry_evaluator=telemetry_evaluator,
        observation_coordinator=observation_coordinator,
        brain_usage_adapter=brain_usage_adapter,
    )

    usage = LLMUsageRecord(
        request_id="handler-test-004",
        user_id="1004",
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
        estimated_cost=0.05,
        latency=1.0,
        success=False,
        error="TEST_FAILURE",
    )

    handler.handle(usage)

    brain_usage_adapter.settle.assert_not_called()


def test_handler_does_not_settle_without_user_id():
    persistence = Mock()
    telemetry_evaluator = Mock()
    observation_coordinator = Mock()
    brain_usage_adapter = Mock()

    telemetry_evaluator.evaluate.return_value = None

    handler = LLMUsageRecordHandler(
        persistence=persistence,
        telemetry_evaluator=telemetry_evaluator,
        observation_coordinator=observation_coordinator,
        brain_usage_adapter=brain_usage_adapter,
    )

    usage = LLMUsageRecord(
        request_id="handler-test-005",
        user_id=None,
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
        estimated_cost=0.05,
        latency=1.0,
        success=True,
    )

    handler.handle(usage)

    brain_usage_adapter.settle.assert_not_called()


def test_handler_does_not_settle_without_execution_cost():
    persistence = Mock()
    telemetry_evaluator = Mock()
    observation_coordinator = Mock()
    brain_usage_adapter = Mock()

    telemetry_evaluator.evaluate.return_value = None

    handler = LLMUsageRecordHandler(
        persistence=persistence,
        telemetry_evaluator=telemetry_evaluator,
        observation_coordinator=observation_coordinator,
        brain_usage_adapter=brain_usage_adapter,
    )

    usage = LLMUsageRecord(
        request_id="handler-test-006",
        user_id="1006",
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
        estimated_cost=None,
        latency=1.0,
        success=True,
    )

    handler.handle(usage)

    brain_usage_adapter.settle.assert_not_called()