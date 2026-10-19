from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterator
from brain.llm.llm_request_context import LLMRequestContext



@dataclass(frozen=True)
class LLMUsage:
    """
    Normalized usage information returned by an LLM provider.
    Provider-specific SDK objects must not cross this boundary.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None


@dataclass(frozen=True)
class LLMResponse:
    """
    Provider-independent LLM response.
    """

    content: str
    usage: LLMUsage | None = None
    provider: str | None = None
    model: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class LLMService(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """
        Returns a Python dictionary.
        """
        pass