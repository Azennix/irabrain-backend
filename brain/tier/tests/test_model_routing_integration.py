from types import SimpleNamespace

from brain.tier.capabilities import Capability
from brain.tier.capability_resolver import CapabilityResolver
from brain.tier.model_definition import ModelDefinition
from brain.tier.model_registry import ModelRegistry
from brain.tier.model_router import ModelRouter
from brain.tier.models import BrainTier


def create_registry():
    registry = ModelRegistry()

    registry.register(
        ModelDefinition(
            model_id="basic-model",
            provider="test-provider",
            capabilities=frozenset({
                Capability.BASIC_CHAT,
                Capability.REASONING,
            }),
            context_window=64000,
            available=True,
        )
    )

    registry.register(
        ModelDefinition(
            model_id="reasoning-model",
            provider="test-provider",
            capabilities=frozenset({
                Capability.BASIC_CHAT,
                Capability.REASONING,
            }),
            context_window=128000,
            reasoning_strength=1.0,
            available=True,
        )
    )

    return registry


def test_full_reasoning_routing_chain():
    analysis = SimpleNamespace(
        requires_memory_retrieval=False,
        confidence=0.9,
    )

    intent = SimpleNamespace(
        requires_tool=False,
        requires_reasoning=True,
        requires_memory=False,
        confidence=0.95,
    )

    capability_requirement = CapabilityResolver.resolve(
        analysis=analysis,
        intent=intent,
    )

    assert capability_requirement.capability == Capability.REASONING

    router = ModelRouter(create_registry())

    selected_model = router.route(
        tier=BrainTier.FREE,
        requirement=capability_requirement,
    )

    assert selected_model.capabilities.__contains__(Capability.REASONING)

    print("FULL REASONING ROUTING CHAIN PASS")


def test_full_basic_chat_routing_chain():
    analysis = SimpleNamespace(
        requires_memory_retrieval=False,
        confidence=0.9,
    )

    intent = SimpleNamespace(
        requires_tool=False,
        requires_reasoning=False,
        requires_memory=False,
        confidence=0.95,
    )

    capability_requirement = CapabilityResolver.resolve(
        analysis=analysis,
        intent=intent,
    )

    assert capability_requirement.capability == Capability.BASIC_CHAT

    router = ModelRouter(create_registry())

    selected_model = router.route(
        tier=BrainTier.FREE,
        requirement=capability_requirement,
    )

    assert Capability.BASIC_CHAT in selected_model.capabilities

    print("FULL BASIC CHAT ROUTING CHAIN PASS")


if __name__ == "__main__":
    test_full_reasoning_routing_chain()
    test_full_basic_chat_routing_chain()
    print("\nMODEL ROUTING INTEGRATION TESTS PASS")