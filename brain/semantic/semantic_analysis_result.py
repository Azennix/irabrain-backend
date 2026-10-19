from dataclasses import dataclass, field
from typing import Any, Optional

from brain.memory.message_analysis_result import (
    MessageType,
    ConversationScore,
)
from decision.intent_result import IntentType


@dataclass(slots=True)
class SemanticAnalysisResult:

    # =================================================
    # MESSAGE
    # =================================================

    message_type: MessageType

    # =================================================
    # INTENT
    # =================================================

    intent: IntentType

    intent_confidence: float = 0.0

    entities: dict[str, Any] = field(
        default_factory=dict
    )

    # =================================================
    # CAPABILITIES
    # =================================================

    requires_reasoning: bool = False

    requires_memory: bool = False

    requires_tool: bool = False

    # =================================================
    # MEMORY
    # =================================================

    should_enter_memory_pipeline: bool = False

    # IMPORTANT:
    # Memory retrieval remains ALWAYS-ON.
    # This field is NOT used to decide retrieval.
    requires_memory_retrieval: bool = True

    # =================================================
    # LANGUAGE
    # =================================================

    language: str = "en"

    script: str = "latin"

    is_mixed: bool = False

    secondary_language: Optional[str] = None

    is_transliterated: bool = False

    tone: str = "neutral"

    response_style: str = "standard"

    # =================================================
    # RESPONSE
    # =================================================

    requires_llm: bool = True

    # =================================================
    # CONFIDENCE
    # =================================================

    confidence: float = 0.0

    # =================================================
    # CONVERSATION
    # =================================================

    conversation_scores: list[ConversationScore] = field(
        default_factory=list
    )