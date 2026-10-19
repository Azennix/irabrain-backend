from unittest.mock import Mock

from openai import APIConnectionError

from brain.llm.llm_service import LLMResponse
from brain.tier.capabilities import Capability
from brain.tier.model_definition import ModelDefinition
from brain.tier.model_fallback_executor import ModelFallbackExecutor


class FakeService:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def generate(
        self,
        prompt,
        *,
        request_context=None,
        system_prompt=None,
        temperature=0.0,
        max_tokens=None,
    ):
        if self.error is not None:
            raise self.error

        return self.response


def test_fallback_executor_uses_next_model_after_retryable_error():
    primary = ModelDefinition(
        model_id="primary-model",
        provider="provider-a",
        capabilities=frozenset({Capability.BASIC_CHAT}),
    )

    fallback = ModelDefinition(
        model_id="fallback-model",
        provider="provider-b",
        capabilities=frozenset({Capability.BASIC_CHAT}),
    )

    success_response = LLMResponse(
        content="Fallback model succeeded.",
        provider="provider-b",
        model="fallback-model",
    )

    connection_error = APIConnectionError(
        request=Mock()
    )

    services = {
        "primary-model": FakeService(
            error=connection_error
        ),
        "fallback-model": FakeService(
            response=success_response
        ),
    }

    executor = ModelFallbackExecutor(
        service_factory=lambda model: services[model.model_id]
    )

    response = executor.execute(
        models=(primary, fallback),
        prompt="Hello",
    )

    assert response.content == "Fallback model succeeded."
    assert response.model == "fallback-model"

    print("FALLBACK EXECUTOR PASS")


def test_fallback_executor_does_not_fallback_on_non_retryable_error():
    primary = ModelDefinition(
        model_id="primary-model",
        provider="provider-a",
        capabilities=frozenset({Capability.BASIC_CHAT}),
    )

    fallback = ModelDefinition(
        model_id="fallback-model",
        provider="provider-b",
        capabilities=frozenset({Capability.BASIC_CHAT}),
    )

    fallback_service = FakeService(
        response=LLMResponse(
            content="This should not execute.",
            provider="provider-b",
            model="fallback-model",
        )
    )

    services = {
        "primary-model": FakeService(
            error=PermissionError("Not allowed")
        ),
        "fallback-model": fallback_service,
    }

    executor = ModelFallbackExecutor(
        service_factory=lambda model: services[model.model_id]
    )

    try:
        executor.execute(
            models=(primary, fallback),
            prompt="Hello",
        )
    except PermissionError:
        print("NON-RETRYABLE ERROR PASS")
        return

    raise AssertionError(
        "Fallback should not execute for non-retryable errors."
    )


if __name__ == "__main__":
    test_fallback_executor_uses_next_model_after_retryable_error()