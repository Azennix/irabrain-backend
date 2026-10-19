from unittest.mock import Mock

from openai import APIConnectionError

from brain.llm.llm_service import LLMResponse
from brain.tier.capabilities import Capability
from brain.tier.model_definition import ModelDefinition
from brain.tier.model_fallback_executor import ModelFallbackExecutor
from brain.tier.model_registry import ModelRegistry
from brain.tier.model_router import ModelRouter
from brain.tier.models import BrainTier
from brain.tier.capability_requirement import CapabilityRequirement


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


def create_registry():
    registry = ModelRegistry()

    registry.register(
        ModelDefinition(
            model_id="primary-model",
            provider="provider-a",
            capabilities=frozenset({
                Capability.BASIC_CHAT,
            }),
            context_window=64000,
            available=True,
        )
    )

    registry.register(
        ModelDefinition(
            model_id="fallback-model",
            provider="provider-b",
            capabilities=frozenset({
                Capability.BASIC_CHAT,
            }),
            context_window=64000,
            available=True,
        )
    )

    return registry


def test_routing_candidates_feed_fallback_executor():
    registry = create_registry()
    router = ModelRouter(registry)

    requirement = CapabilityRequirement(
        capability=Capability.BASIC_CHAT,
    )

    candidates = router.route_candidates(
        tier=BrainTier.FREE,
        requirement=requirement,
    )

    assert len(candidates) == 2

    primary = candidates[0]
    fallback = candidates[1]

    services = {
        primary.model_id: FakeService(
            error=APIConnectionError(request=Mock())
        ),
        fallback.model_id: FakeService(
            response=LLMResponse(
                content="Fallback succeeded.",
                provider=fallback.provider,
                model=fallback.model_id,
            )
        ),
    }

    executor = ModelFallbackExecutor(
        service_factory=lambda model: services[model.model_id]
    )

    response = executor.execute(
        models=candidates,
        prompt="Hello",
    )

    assert response.content == "Fallback succeeded."
    assert response.model == fallback.model_id

    print("ROUTING + FALLBACK PASS")


if __name__ == "__main__":
    test_routing_candidates_feed_fallback_executor()
    print("\nMODEL ROUTING FALLBACK INTEGRATION PASS")