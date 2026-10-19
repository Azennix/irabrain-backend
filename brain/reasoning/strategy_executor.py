from brain.reasoning.reasoning_result import ReasoningResult
from brain.reasoning.strategies import ReasoningStrategy
from brain.reasoning.strategy_registry import STRATEGY_CONTRACTS


class StrategyExecutor:

    def execute(
        self,
        strategy: ReasoningStrategy,
        conclusion: str,
        confidence: float,
        evidence: list,
        alternatives: list,
        risks: list,
        assumptions: list,
    ) -> ReasoningResult:

        contract = STRATEGY_CONTRACTS.get(strategy)

        if contract is None:
            strategy = ReasoningStrategy.DIRECT
            contract = STRATEGY_CONTRACTS[strategy]

        result = self._result(
            strategy,
            conclusion,
            confidence,
            evidence,
            alternatives,
            risks,
            assumptions,
        )

        violations = contract.validate(result)

        if violations:

            print(
                "\n===== STRATEGY CONTRACT VIOLATIONS ====="
            )

            for violation in violations:
                print(
                    "VIOLATION:",
                    violation
                )

            print(
                "========================================\n"
            )

        return result

    @staticmethod
    def _result(
        strategy,
        conclusion,
        confidence,
        evidence,
        alternatives,
        risks,
        assumptions,
    ):
        return ReasoningResult(
            strategy=strategy,
            conclusion=conclusion,
            confidence=confidence,
            evidence=evidence,
            alternatives=alternatives,
            risks=risks,
            assumptions=assumptions,
        )