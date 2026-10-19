from dataclasses import dataclass, field

from brain.memory.memory_model import Memory


@dataclass(slots=True)
class ResolutionPlan:

    insert: list[Memory] = field(default_factory=list)

    update: list[Memory] = field(default_factory=list)

    merge: list[Memory] = field(default_factory=list)

    ignore: list[Memory] = field(default_factory=list)