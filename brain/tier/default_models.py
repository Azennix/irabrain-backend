from brain.tier.capabilities import Capability
from brain.tier.model_definition import ModelDefinition
from brain.tier.model_registry import ModelRegistry


def create_default_model_registry() -> ModelRegistry:
    registry = ModelRegistry()

    registry.register(
        ModelDefinition(
            model_id="deepseek-flash",
            provider="deepseek",
            capabilities=frozenset(
                {
                    Capability.BASIC_CHAT,
                    Capability.REASONING,
                    Capability.CODING,
                    Capability.ANALYSIS,
                    Capability.MEMORY,
                    Capability.LARGE_CONTEXT,
                }
            ),
            context_window=64000,
            available=True,
        )
    )

    return registry