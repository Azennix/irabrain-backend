from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class BrainRequest:
    """
    Standard request object shared across all IRABRAIN engines.
    """

    user_id: int
    query: str

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    conversation_id: str | None = None
    project_id: str | None = None
    session_id: str | None = None

    language: str = "auto"

    attachments: list[Any] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )