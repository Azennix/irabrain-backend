from enum import Enum


class ReasoningStrategy(str, Enum):

    DIRECT = "direct"

    ANALYSIS = "analysis"

    COMPARISON = "comparison"

    DECISION = "decision"

    PLANNING = "planning"

    PROBLEM_SOLVING = "problem_solving"