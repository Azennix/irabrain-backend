from collections.abc import Callable
from typing import Any

from brain.llm.llm_service import (
    LLMService,
    LLMResponse,
)
from brain.llm.llm_request_context import LLMRequestContext

from brain.tier.model_definition import ModelDefinition
from brain.tier.model_fallback_policy import ModelFallbackPolicy


class ModelFallbackExecutor:
    def __init__(
        self,
        service_factory: Callable[[ModelDefinition], LLMService],
    ):
        if service_factory is None:
            raise ValueError("Service factory is required.")

        self.service_factory = service_factory

    def execute(
        self,
        models: tuple[ModelDefinition, ...],
        prompt: str,
        request_context: LLMRequestContext | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        if not models:
            raise ValueError("At least one model is required.")

        last_error: Exception | None = None

        for model in models:
            service = self.service_factory(model)

            try:
                return service.generate(
                    prompt=prompt,
                    request_context=request_context,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

            except Exception as error:
                if not ModelFallbackPolicy.is_retryable(error):
                    raise

                last_error = error

        if last_error is not None:
            raise last_error

        raise RuntimeError("Model fallback execution failed.")