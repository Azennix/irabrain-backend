from brain.tier.capabilities import Capability
from brain.tier.model_definition import ModelDefinition


class ModelRegistry:
    def __init__(self):
        self._models: dict[str, ModelDefinition] = {}

    def register(self, model: ModelDefinition) -> None:
        if model.model_id in self._models:
            raise ValueError(
                f"Model already registered: {model.model_id}"
            )

        self._models[model.model_id] = model

    def get(self, model_id: str) -> ModelDefinition | None:
        return self._models.get(model_id)

    def all(self) -> tuple[ModelDefinition, ...]:
        return tuple(self._models.values())

    def available(self) -> tuple[ModelDefinition, ...]:
        return tuple(
            model
            for model in self._models.values()
            if model.available
        )

    def find_by_capability(
        self,
        capability: Capability,
    ) -> tuple[ModelDefinition, ...]:
        return tuple(
            model
            for model in self.available()
            if capability in model.capabilities
        )