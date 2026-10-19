from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class ConversationMessage:

    message_id: str

    user_id: int

    role: str
    content: str

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )