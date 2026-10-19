from brain.tier.model_definition import ModelDefinition


class ModelScorer:
    @staticmethod
    def score(
        model: ModelDefinition,
        max_context_window: int,
        max_latency_score: float,
        max_cost_per_unit: float,
        complexity: float = 0.0,
    ) -> float:
        if model is None:
            raise ValueError("Model is required.")

        if max_context_window <= 0:
            raise ValueError("max_context_window must be greater than zero.")

        if max_latency_score < 0:
            raise ValueError("max_latency_score cannot be negative.")

        if max_cost_per_unit < 0:
            raise ValueError("max_cost_per_unit cannot be negative.")

        if not 0.0 <= complexity <= 1.0:
            raise ValueError(
                "complexity must be between 0.0 and 1.0."
            )

        context_score = (
            model.context_window / max_context_window
        )

        latency_score = (
            1.0
            if max_latency_score == 0
            else max (
                0.0,
                1.0 -(
                model.latency_score / max_latency_score
                ),
            )

        )

        cost_score = (
            1.0
            if max_cost_per_unit == 0
            else max(
                0.0,
                1.0 - (
                    model.cost_per_unit / max_cost_per_unit
            ),
            )

        )

        context_weight = 0.3 + (0.2 * complexity)
        latency_weight = 0.4 - (0.2 * complexity)
        cost_weight = 0.3

        return (
           (context_score * context_weight)
           + (latency_score * latency_weight)
           + (cost_score * cost_weight)
)