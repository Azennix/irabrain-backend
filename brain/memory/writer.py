from brain.memory.repository import MemoryRepository
from brain.memory.resolution_plan import ResolutionPlan


class MemoryWriter:

    def __init__(
        self,
        repository: MemoryRepository
    ):
        self.repository = repository

    def write(
        self,
        plan: ResolutionPlan
    ):

        for memory in plan.insert:

            if memory is None:
                continue

            self.repository.insert(memory)

        for memory in plan.update:

            if memory is None:
                continue

            self.repository.update(memory)

        return plan