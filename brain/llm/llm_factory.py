from __future__ import annotations

import os

from brain.llm.deepseek_service import DeepSeekService
from brain.llm.llm_service import LLMService
from brain.llm.tracked_llm_service import TrackedLLMService
from brain.llm.usage_tracker import UsageTracker


class LLMFactory:
    @staticmethod
    def create_chat_service(
        usage_tracker: UsageTracker | None = None,
        provider: str = "deepseek",
        model: str = "deepseek-flash",
        cost_resolver=None,
    ) -> LLMService:

        provider_name = provider.lower().strip()

        if provider_name == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")

            if not api_key:
                raise RuntimeError(
                    "DEEPSEEK_API_KEY is not configured."
                )

            service = DeepSeekService(
                model=model,
                api_key=api_key,
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}"
            )

        if usage_tracker is None:
            return service

        return TrackedLLMService(
            provider=service,
            usage_tracker=usage_tracker,
            cost_resolver=cost_resolver,
        )