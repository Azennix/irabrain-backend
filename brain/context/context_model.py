from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Context:

    """
    Unified context passed to downstream IRABrain components.

    Contains:

    - long-term memory context
    - recent conversation history
    """

    # =====================================================
    # LONG-TERM MEMORY
    # =====================================================

    memory: dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # CONVERSATION HISTORY
    # =====================================================

    conversation: list[Any] = field(
        default_factory=list
    )

    # =====================================================
    # CONVERSATION SUMMARY
    # =====================================================

    conversation_summary: str | None = None