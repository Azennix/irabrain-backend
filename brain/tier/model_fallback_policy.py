from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    RateLimitError,
)


class ModelFallbackPolicy:
    @staticmethod
    def is_retryable(error: Exception) -> bool:
        if isinstance(
            error,
            (
                RateLimitError,
                APITimeoutError,
                APIConnectionError,
            ),
        ):
            return True

        if isinstance(error, APIError):
            return True

        return False