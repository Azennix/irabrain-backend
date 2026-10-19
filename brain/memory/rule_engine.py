from brain.base.brain_request import BrainRequest
from brain.memory.rule_result import RuleResult
from brain.memory.rules.identity_rule import IdentityRule


class RuleEngine:

    def __init__(self):

        self.rules = [

            IdentityRule()

        ]

    def extract(
        self,
        request: BrainRequest
    ) -> RuleResult:

        for rule in self.rules:

            result = rule.execute(request)

            if result.matched:

                return result

        return RuleResult(
            matched=False
        )