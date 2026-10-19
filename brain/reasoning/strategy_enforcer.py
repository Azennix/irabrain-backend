from brain.reasoning.reasoning_result import ReasoningResult
from brain.reasoning.strategy_registry import STRATEGY_CONTRACTS


class StrategyEnforcer:

    def enforce(
        self,
        result: ReasoningResult
    ) -> ReasoningResult:

        contract = STRATEGY_CONTRACTS.get(
            result.strategy
        )

        if contract is None:
            result.confidence = 0.0
            return result

        violations = contract.validate(
            result
        )

        if not violations:
            return result

        print(
            "\n===== STRATEGY ENFORCEMENT ====="
        )

        for violation in violations:
            print(
                "VIOLATION:",
                violation
            )

        print(
            "Action: confidence downgraded"
        )

        print(
            "================================\n"
        )

        result.confidence = 0.0

        return result