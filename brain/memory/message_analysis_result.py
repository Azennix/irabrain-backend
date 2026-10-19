from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MessageType(str, Enum):
    UNKNOWN = "UNKNOWN"
    CHAT = "CHAT"
    QUESTION = "QUESTION"
    COMMAND = "COMMAND"
    MEMORY = "MEMORY"
    TASK = "TASK"


@dataclass(slots=True)
class ConversationScore:

    message_id: str

    score: float

    reasoning: str = ""


@dataclass(slots=True)
class MessageAnalysisResult:

    # =================================================
    # MESSAGE
    # =================================================

    message_type: MessageType

    # =================================================
    # MEMORY DECISIONS
    # =================================================

    # Should this message potentially be SAVED as memory?
    should_enter_memory_pipeline: bool

    # Does this message require SEARCHING existing memories?
    requires_memory_retrieval: bool

    # =================================================
    # LLM
    # =================================================

    requires_llm: bool

    confidence: float

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
    # CONVERSATION RELEVANCE
    # =================================================

    conversation_scores: list[ConversationScore] = field(
        default_factory=list
    )