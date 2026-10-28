from __future__ import annotations

import os
from typing import Any, Iterator

from dotenv import load_dotenv
from openai import OpenAI

from brain.llm.llm_request_context import LLMRequestContext
from brain.llm.llm_service import (
    LLMResponse,
    LLMService,
    LLMUsage,
)
from openai import OpenAI, APIConnectionError, APITimeoutError



load_dotenv()


class DeepSeekService(LLMService):
    """
    DeepSeek implementation of the IRABRAIN LLMService contract.

    DeepSeek is accessed through its OpenAI-compatible API.
    """

    def __init__(
        self,
        model: str = "deepseek-flash",
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com",
    ):
        self.model = model
        self.base_url = base_url

        resolved_api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

        if not resolved_api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=resolved_api_key,
            base_url=base_url,
            timeout=90.0,
            max_retries=2,
        )

        self.last_stream_response: LLMResponse | None = None

    # =========================================================
    # NORMAL GENERATION
    # =========================================================

    def generate(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext | None = None,
        **kwargs: Any,
    ) -> LLMResponse:

        system_prompt = kwargs.pop("system_prompt", None)
        max_tokens = kwargs.pop("max_tokens", None)

        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        request_kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            **kwargs,
        }

        if max_tokens is not None:
            request_kwargs["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(
            **request_kwargs,
        )

        content = response.choices[0].message.content or ""

        usage = self._extract_usage(response)

        return LLMResponse(
            content=content,
            usage=usage,
            provider="deepseek",
            model=self.model,
            metadata={
                "base_url": self.base_url,
                "request_id": (
                    request_context.request_id
                    if request_context
                    else None
                ),
            },
        )

    # =========================================================
    # STREAMING GENERATION
    # =========================================================

    def generate_stream(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:

        self.last_stream_response = None

        system_prompt = kwargs.pop("system_prompt", None)

        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
            }
        )

        messages.append(
            {
                "role": "user",
                "content": prompt,
        }
    )

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
            **kwargs,
    )

        full_content = ""
        final_usage: LLMUsage | None = None

        try:
            for chunk in stream:
                usage = getattr(chunk, "usage", None)

                if usage is not None:
                    final_usage = self._convert_usage(usage)

                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)

                if content:
                    full_content += content
                    yield content

        # IMPORTANT: Save the final response after successful streaming.
            self.last_stream_response = LLMResponse(
                content=full_content,
                usage=final_usage,
                provider="deepseek",
                model=self.model,
                metadata={
                    "base_url": self.base_url,
                    "request_id": (
                        request_context.request_id
                        if request_context
                        else None
                    ),
                    "stream_interrupted": False,
            },
        )

        except (APIConnectionError, APITimeoutError):
            self.last_stream_response = LLMResponse(
                content=full_content,
                usage=final_usage,
                provider="deepseek",
                model=self.model,
                metadata={
                    "base_url": self.base_url,
                    "request_id": (
                        request_context.request_id
                        if request_context
                        else None
                ),
                    "stream_interrupted": True,
            },
        )
            raise

        finally:
            stream.close()

    # =========================================================
    # STRUCTURED GENERATION
    # =========================================================

    def _generate_structured_response(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> LLMResponse:
        import json

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            stream=False,
            temperature=temperature,
            **kwargs,
        )

        content = response.choices[0].message.content or "{}"

        # Validate JSON before reporting the provider call as successful.
        json.loads(content)

        return LLMResponse(
            content=content,
            usage=self._extract_usage(response),
            provider="deepseek",
            model=self.model,
            metadata={
                "request_id": (
                    request_context.request_id
                    if request_context is not None
                    else None
                ),
            },
        )

    def generate_structured(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        import json

        response = self._generate_structured_response(
            prompt,
            request_context=request_context,
            system_prompt=kwargs.pop("system_prompt", None),
            temperature=kwargs.pop("temperature", 0.0),
            **kwargs,
        )
        return json.loads(response.content)

    # =========================================================
    # USAGE EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_usage(
        response: Any,
    ) -> LLMUsage | None:

        usage = getattr(
            response,
            "usage",
            None,
        )

        if usage is None:
            return None

        return DeepSeekService._convert_usage(
            usage
        )

    # =========================================================
    # USAGE CONVERSION
    # =========================================================

    @staticmethod
    def _convert_usage(
        usage: Any,
    ) -> LLMUsage:

        input_tokens = getattr(
            usage,
            "prompt_tokens",
            None,
        )

        output_tokens = getattr(
            usage,
            "completion_tokens",
            None,
        )

        total_tokens = getattr(
            usage,
            "total_tokens",
            None,
        )

        cached_tokens = getattr(
            usage,
            "prompt_cache_hit_tokens",
            None,
        )

        reasoning_tokens = None

        completion_details = getattr(
            usage,
            "completion_tokens_details",
            None,
        )

        if completion_details is not None:
            reasoning_tokens = getattr(
                completion_details,
                "reasoning_tokens",
                None,
            )

        return LLMUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
        )