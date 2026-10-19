from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Memory:

    # Unique ID
    memory_id: str

    # Owner
    user_id: int

    # Memory Classification
    category: str
    key: str

    # Actual Information
    value: Any



    # AI Confidence (0.0 - 1.0)
    confidence: float

    embedding: list[float] | None = None

    association_embedding: list[float] | None = None

    # Where this memory came from
    source: str = "conversation"

    # Importance Score
    importance: float = 0.5

    # Retrieval relevance for the current query
    retrieval_score: float = 0.0

    # Last Access Time
    last_accessed: datetime | None = None

    # How many times useda
    access_count: int = 0

    # Creation Time
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Last Update Time
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Extra Information
    metadata: dict[str, Any] = field(default_factory=dict)