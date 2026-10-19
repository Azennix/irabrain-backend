from brain.reasoning.strategies import ReasoningStrategy
from brain.reasoning.strategy_contract import StrategyContract


STRATEGY_CONTRACTS = {

    ReasoningStrategy.DIRECT:
        StrategyContract(
            strategy=ReasoningStrategy.DIRECT
        ),

    ReasoningStrategy.ANALYSIS:
        StrategyContract(
            strategy=ReasoningStrategy.ANALYSIS,
            requires_assumptions=True
        ),

    ReasoningStrategy.COMPARISON:
        StrategyContract(
            strategy=ReasoningStrategy.COMPARISON,
            requires_alternatives=True,
            requires_risks=True
        ),

    ReasoningStrategy.DECISION:
        StrategyContract(
            strategy=ReasoningStrategy.DECISION,
            requires_alternatives=True,
            requires_risks=True,
            requires_assumptions=True
        ),

    ReasoningStrategy.PLANNING:
        StrategyContract(
            strategy=ReasoningStrategy.PLANNING,
            requires_assumptions=True
        ),

    ReasoningStrategy.PROBLEM_SOLVING:
        StrategyContract(
            strategy=ReasoningStrategy.PROBLEM_SOLVING,
            requires_risks=True,
            requires_assumptions=True
        ),
}