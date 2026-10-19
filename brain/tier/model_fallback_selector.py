from brain.tier.model_definition import ModelDefinition


class ModelFallbackSelector:
    @staticmethod
    def select_all(
        models: tuple[ModelDefinition, ...],
        failed_model_id: str,
    ) -> tuple[ModelDefinition, ...]:
        if not models:
            return ()

        return tuple(
            model
            for model in models
            if (
                model.model_id != failed_model_id
                and model.available
            )
        )

    @staticmethod
    def select(
        models: tuple[ModelDefinition, ...],
        failed_model_id: str,
    ) -> ModelDefinition | None:
        candidates = ModelFallbackSelector.select_all(
            models=models,
            failed_model_id=failed_model_id,
        )

        if not candidates:
            return None

        return candidates[0]