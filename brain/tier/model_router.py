from brain.tier.capability_policy import CapabilityPolicy
from brain.tier.capability_requirement import CapabilityRequirement
from brain.tier.model_definition import ModelDefinition
from brain.tier.model_registry import ModelRegistry
from brain.tier.model_scorer import ModelScorer
from brain.tier.models import BrainTier


class ModelRouter:
    def __init__(self, registry: ModelRegistry):
        if registry is None:
            raise ValueError("Model registry is required.")

        self.registry = registry

    def route(
        self,
        tier: BrainTier,
        requirement: CapabilityRequirement,
    ) -> ModelDefinition:
        candidates = self.route_candidates(
            tier=tier,
            requirement=requirement,
        )

        return candidates[0]


    def route_candidates(
        self,
        tier: BrainTier,
        requirement: CapabilityRequirement,
    ) -> tuple[ModelDefinition, ...]:
        if not CapabilityPolicy.allows(
            tier,
            requirement.capability,
        ):
            raise PermissionError(
                f"Brain tier {tier.value} does not allow "
                f"capability {requirement.capability.value}."
            )

        models = self.registry.find_by_capability(
            requirement.capability
        )

        models = tuple(
            model
            for model in models
            if (
                model.context_window
                >= requirement.required_context_window
                and model.reasoning_strength
                >= requirement.complexity
            )
        )

        if not models:
            raise LookupError(
                f"No available model supports capability "
                f"{requirement.capability.value} with the "
                f"required routing constraints."
            )

        max_context_window = max(
            model.context_window
            for model in models
        )

        max_latency_score = max(
            model.latency_score
            for model in models
        )

        max_cost_per_unit = max(
            model.cost_per_unit
            for model in models
        )

        scored_models = [
            (
                ModelScorer.score(
                    model=model,
                    max_context_window=max_context_window,
                    max_latency_score=max_latency_score,
                    max_cost_per_unit=max_cost_per_unit,
                    complexity=requirement.complexity,
                ),
                model,
            )
            for model in models
        ]

        scored_models.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return tuple(
            model
            for _, model in scored_models
        )