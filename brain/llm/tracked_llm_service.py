import time

from brain.llm.llm_service import (
    LLMService,
    LLMResponse,
    LLMUsage,
)

from brain.llm.usage import LLMUsageRecord
from brain.llm.usage_tracker import UsageTracker
from brain.llm.llm_request_context import LLMRequestContext
from brain.recharge.models import BrainUsageContext


class TrackedLLMService(LLMService):

    def __init__(
        self,
        provider: LLMService,
        usage_tracker: UsageTracker,
        cost_resolver=None,
    ):
        self.provider = provider
        self.usage_tracker = usage_tracker
        self.cost_resolver = cost_resolver

    # =====================================================
    # EXECUTION COST
    # =====================================================

    def _resolve_execution_cost(
        self,
        *,
        request_id: str,
        user_id: int | None,
        provider: str,
        model: str,
        input_tokens: int | None,
        output_tokens: int | None,
        cached_tokens: int | None,
        reasoning_tokens: int | None,
        total_tokens: int | None,
    ) -> float | None:

        if self.cost_resolver is None:
            return None

        context = BrainUsageContext(
            request_id=request_id,
            user_id=user_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            total_tokens=total_tokens,
        )

        cost = self.cost_resolver.resolve(context)

        if cost is None:
            return None

        return float(cost.amount)

    # =====================================================
    # NORMAL RESPONSE
    # =====================================================

    def generate(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> LLMResponse:

        request_id = request_context.request_id
        user_id = request_context.user_id

        start_time = time.perf_counter()

        try:

            response = self.provider.generate(
                prompt,
                request_context=request_context,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            latency = time.perf_counter() - start_time

            usage = response.usage

            provider_name = response.provider or "unknown"
            model_name = response.model or "unknown"

            input_tokens = (
                usage.input_tokens
                if usage
                else None
            )

            output_tokens = (
                usage.output_tokens
                if usage
                else None
            )

            cached_tokens = (
                usage.cached_tokens
                if usage
                else None
            )

            reasoning_tokens = (
                usage.reasoning_tokens
                if usage
                else None
            )

            total_tokens = (
                usage.total_tokens
                if usage
                else None
            )

            execution_cost = self._resolve_execution_cost(
                request_id=request_id,
                user_id=user_id,
                provider=provider_name,
                model=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
                reasoning_tokens=reasoning_tokens,
                total_tokens=total_tokens,
            )

            self.usage_tracker.record(
                LLMUsageRecord(
                    request_id=request_id,
                    user_id=user_id,
                    provider=provider_name,
                    model=model_name,
                    brain_tier=request_context.brain_tier,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cached_tokens=cached_tokens,
                    reasoning_tokens=reasoning_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=execution_cost,
                    latency=latency,
                    success=True,
                )
            )

            return response

        except Exception as error:

            latency = time.perf_counter() - start_time

            self.usage_tracker.record(
                LLMUsageRecord(
                    request_id=request_id,
                    user_id=user_id,
                    provider="unknown",
                    model="unknown",
                    brain_tier=request_context.brain_tier,
                    latency=latency,
                    success=False,
                    error=str(error),
                )
            )

            raise

    # =====================================================
    # STREAMING RESPONSE
    # =====================================================

    def generate_stream(
        self,
        prompt: str,
        *,
        request_context: LLMRequestContext | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ):

        start_time = time.perf_counter()

        request_id = (
            request_context.request_id
            if request_context
            else None
        )

        user_id = (
            request_context.user_id
            if request_context
            else None
        )

        try:

            # -------------------------------------------------
            # Start provider stream
            # -------------------------------------------------

            stream = self.provider.generate_stream(
                prompt,
                request_context=request_context,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # -------------------------------------------------
            # Forward chunks to caller
            # -------------------------------------------------

            for chunk in stream:
                yield chunk

            # -------------------------------------------------
            # Provider has completed streaming.
            #
            # DeepSeekService stores the final typed
            # LLMResponse in last_stream_response.
            # -------------------------------------------------

            latency = time.perf_counter() - start_time

            final_response = getattr(
                self.provider,
                "last_stream_response",
                None,
            )

            # -------------------------------------------------
            # Default values
            # -------------------------------------------------

            usage = None
            provider_name = "unknown"
            model_name = "unknown"

            # -------------------------------------------------
            # Read typed LLMResponse
            # -------------------------------------------------

            if isinstance(
                final_response,
                LLMResponse,
            ):

                provider_name = (
                    final_response.provider
                    or "unknown"
                )

                model_name = (
                    final_response.model
                    or "unknown"
                )

                usage = final_response.usage

            # -------------------------------------------------
            # Extract usage
            # -------------------------------------------------

            input_tokens = (
                usage.input_tokens
                if usage
                else None
            )

            output_tokens = (
                usage.output_tokens
                if usage
                else None
            )

            cached_tokens = (
                usage.cached_tokens
                if usage
                else None
            )

            reasoning_tokens = (
                usage.reasoning_tokens
                if usage
                else None
            )

            total_tokens = (
                usage.total_tokens
                if usage
                else None
            )

            # -------------------------------------------------
            # Resolve real execution cost
            # -------------------------------------------------

            execution_cost = None

            if request_id is not None:

                execution_cost = (
                    self._resolve_execution_cost(
                        request_id=request_id,
                        user_id=user_id,
                        provider=provider_name,
                        model=model_name,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cached_tokens=cached_tokens,
                        reasoning_tokens=reasoning_tokens,
                        total_tokens=total_tokens,
                    )
                )

                print(
                    f"\n[LLM DIAGNOSTIC] "
                    f"request_id={request_id} | "
                    f"provider={provider_name} | "
                    f"model={model_name} | "
                    f"input={input_tokens} | "
                    f"output={output_tokens} | "
                    f"reasoning={reasoning_tokens} | "
                    f"total={total_tokens} | "
                    f"cost={execution_cost} | "
                    f"latency={latency:.3f}s"
)

            # -------------------------------------------------
            # Record successful usage
            # -------------------------------------------------

            self.usage_tracker.record(
                LLMUsageRecord(
                    request_id=request_id or "unknown",
                    user_id=user_id,
                    provider=provider_name,
                    model=model_name,
                    brain_tier=request_context.brain_tier,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cached_tokens=cached_tokens,
                    reasoning_tokens=reasoning_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=execution_cost,
                    latency=latency,
                    success=True,
                )
            )

        except Exception as error:

            latency = time.perf_counter() - start_time

            self.usage_tracker.record(
                LLMUsageRecord(
                    request_id=request_id or "unknown",
                    user_id=user_id,
                    provider="unknown",
                    model="unknown",
                    brain_tier=request_context.brain_tier,
                    latency=latency,
                    success=False,
                    error=str(error),
                )
            )

            raise

    # =====================================================
    # STRUCTURED RESPONSE
    # =====================================================

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