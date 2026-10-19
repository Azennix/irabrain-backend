from dataclasses import dataclass, field
from typing import List


@dataclass
class ExecutionPlan:
    """
    Created by the Orchestrator.
    Decides which engines should run.
    """

    engines: List[str] = field(default_factory=list)

    tools: List[str] = field(default_factory=list)

    llm_required: bool = True

    reflection_required: bool = True

    memory_update_required: bool = True