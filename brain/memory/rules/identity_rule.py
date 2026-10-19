from brain.base.brain_request import BrainRequest
from brain.memory.rule_result import RuleResult
from brain.memory.rules.memory_rule import MemoryRule


class IdentityRule(MemoryRule):

    def execute(
        self,
        request: BrainRequest
    ) -> RuleResult:

        return RuleResult(
            matched=False
        )