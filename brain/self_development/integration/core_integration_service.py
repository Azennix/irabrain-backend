from typing import Callable, Optional

from brain.self_development.integration.core_execution_signal import (
    CoreExecutionSignal,
)


class CoreIntegrationService:
    """
    Boundary between IRABRAIN Core and the separate
    Self-Development system.

    This service receives Core execution signals
    and forwards them to the Self-Development gateway.

    It does not execute self-development actions.
    """

    def __init__(
        self,
        signal_handler: Optional[
            Callable[[CoreExecutionSignal], None]
        ] = None,
    ):
        self.signal_handler = signal_handler

    def publish(
        self,
        signal: CoreExecutionSignal,
    ) -> None:
        if signal is None:
            raise ValueError(
                "Core execution signal cannot be None."
            )

        if self.signal_handler is not None:
            self.signal_handler(signal)