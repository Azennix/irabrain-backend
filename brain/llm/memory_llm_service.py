from brain.llm.llm_service import LLMService
from brain.llm.llm_request_context import LLMRequestContext



class MemoryLLMService(LLMService):

    def __init__(
        self,
        provider: LLMService | None = None
    ):
        if provider is None:
            raise ValueError(
                "MemoryLLMService requires an LLM provider."
    )

        self.provider = provider

    def generate(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> str:

        return self.provider.generate(
            prompt,
            request_context=request_context,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def generate_stream(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ):

        return self.provider.generate_stream(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def generate_structured(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.0,
    ) -> dict:

        return self.provider.generate_structured(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )