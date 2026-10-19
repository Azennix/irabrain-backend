from dataclasses import dataclass, field


@dataclass(slots=True)
class MemoryQuery:

    search_keys: list[str] = field(default_factory=list)

    search_categories: list[str] = field(default_factory=list)