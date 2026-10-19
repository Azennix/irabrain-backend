from dataclasses import dataclass
from enum import Enum


class EvidenceSource(Enum):

    USER_MEMORY = "user_memory"

    CONVERSATION = "conversation"

    CURRENT_REQUEST = "current_request"

    GENERAL_KNOWLEDGE = "general_knowledge"


@dataclass(frozen=True, slots=True)
class Evidence:

    content: str

    source: EvidenceSource

    confidence: float = 1.0

    reference_id: str | None = None