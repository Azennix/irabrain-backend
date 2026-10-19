from typing import Optional


class ConfidenceController:
    """
    Controls whether a confidence notice should be
    attached to the generated response.

    IMPORTANT:

    No reasoning result means that reasoning was not required.
    It does NOT mean that the response has zero confidence.

    Therefore confidence warnings are only applied when
    an actual confidence value is provided.
    """

    def adjust(
        self,
        response: str,
        confidence: Optional[float] = None
    ) -> str:

        # ==========================================
        # EMPTY RESPONSE
        # ==========================================

        if not response:
            return response

        # ==========================================
        # NO CONFIDENCE AVAILABLE
        # ==========================================

        # No reasoning was performed.
        # Do not add a warning.
        if confidence is None:
            return response

        # ==========================================
        # SAFETY / NORMALIZE
        # ==========================================

        confidence = max(
            0.0,
            min(
                1.0,
                float(confidence)
            )
        )

        # ==========================================
        # HIGH CONFIDENCE
        # ==========================================

        if confidence >= 0.75:
            return response

        # ==========================================
        # MEDIUM CONFIDENCE
        # ==========================================

        if confidence >= 0.50:
            return (
                response
                + "\n\n"
                "I'm reasonably confident, but some details "
                "may need verification."
            )

        # ==========================================
        # LOW CONFIDENCE
        # ==========================================

        return (
            response
            + "\n\n"
            "I'm not fully confident about this answer, "
            "so it should be verified before relying on it."
        )