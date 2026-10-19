from brain.reasoning.reasoning_result import ReasoningResult


class ConfidenceEvaluator:

    def evaluate(
        self,
        result: ReasoningResult
    ) -> float:

        if not result:
            return 0.0

        confidence = result.confidence

        # -----------------------------------------
        # Start with model confidence
        # -----------------------------------------

        score = confidence

        # -----------------------------------------
        # Evidence adjustment
        # -----------------------------------------

        if result.evidence:

            evidence_confidence = sum(
                evidence.confidence
                for evidence in result.evidence
            ) / len(result.evidence)

            score = (
                score * 0.70
                + evidence_confidence * 0.30
            )

        # -----------------------------------------
        # No evidence → don't increase confidence
        # -----------------------------------------

        else:
            score = score * 0.85

        # -----------------------------------------
        # Keep confidence inside [0, 1]
        # -----------------------------------------

        return max(
            0.0,
            min(
                1.0,
                score
            )
        )