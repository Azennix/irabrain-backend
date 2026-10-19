from brain.tier.capabilities import Capability
from brain.tier.capability_requirement import CapabilityRequirement
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
            }),
            context_window=64000,
            available=True,
        )
    )

    registry.register(
        ModelDefinition(
            model_id="deep-reasoning-model",
            provider="test-provider",
            capabilities=frozenset({
                Capability.BASIC_CHAT,
                Capability.DEEP_REASONING,
            }),
            context_window=128000,
            reasoning_strength=1.0,
            available=True,
        )
    )

    return registry


def test_free_allows_basic_chat():
    router = ModelRouter(create_registry())

    requirement = CapabilityRequirement(
        capability=Capability.BASIC_CHAT,
    )

    model = router.route(
        tier=BrainTier.FREE,
        requirement=requirement,
    )

    assert model.model_id in {
        "basic-model",
        "deep-reasoning-model",
}

    print("FREE BASIC CHAT PASS")


def test_free_blocks_deep_reasoning():
    router = ModelRouter(create_registry())

    requirement = CapabilityRequirement(
        capability=Capability.DEEP_REASONING,
    )

    try:
        router.route(
            tier=BrainTier.FREE,
            requirement=requirement,
        )
    except PermissionError:
        print("FREE DEEP REASONING BLOCK PASS")
        return

    raise AssertionError(
        "FREE tier should not allow deep reasoning."
    )


def test_thalamus_blocks_deep_reasoning():
    router = ModelRouter(create_registry())

    requirement = CapabilityRequirement(
        capability=Capability.DEEP_REASONING,
    )

    try:
        router.route(
            tier=BrainTier.THALAMUS,
            requirement=requirement,
        )
    except PermissionError:
        print("THALAMUS DEEP REASONING BLOCK PASS")
        return

    raise AssertionError(
        "THALAMUS tier should not allow deep reasoning."
    )


def test_hippocampus_allows_deep_reasoning():
    router = ModelRouter(create_registry())

    requirement = CapabilityRequirement(
        capability=Capability.DEEP_REASONING,
        complexity=0.5,
    )

    model = router.route(
        tier=BrainTier.HIPPOCAMPUS,
        requirement=requirement,
    )

    assert model.model_id == "deep-reasoning-model"

    print("HIPPOCAMPUS DEEP REASONING PASS")


if __name__ == "__main__":
    test_free_allows_basic_chat()
    test_free_blocks_deep_reasoning()
    test_thalamus_blocks_deep_reasoning()
    test_hippocampus_allows_deep_reasoning()

    print("\nMODEL ROUTER TIER TESTS PASS")