# conversation_scorer.py

from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
import json


@dataclass(frozen=True, slots=True)
class ConversationScore:
    message_id: str
    score: float
    is_high_value: bool
    reasoning: str = ""


class ConversationScorer:
    """
    Scores recent conversation messages for short-term contextual value.

    Two layers:

    1. DETERMINISTIC NEAR-REPEAT CHECK (cheap, instant, no LLM)
       Catches the case where the current message is a near-duplicate
       of an earlier message (e.g. "explain python functions" vs
       "bro explain python functions"). These are ALWAYS marked
       high-value, regardless of what the LLM scorer would say --
       this is what makes duplicate-request detection reliable
       instead of depending on an LLM's judgment call every time.

    2. LLM JUDGMENT (one call per turn)
       For everything else, the LLM scores relevance -- this handles
       fuzzy references like "make it better", "why?", "another one"
       that a keyword or similarity check alone can't reliably catch.
    """

    HIGH_VALUE_THRESHOLD = 0.60
    NEAR_REPEAT_THRESHOLD = 0.72  # tune this based on testing

    def __init__(self, llm_service):
        self.llm_service = llm_service

    def score_conversation(
        self,
        messages: list,
        current_message: str
    ) -> list[ConversationScore]:

        if not messages:
            return []

        # -----------------------------------------
        # LAYER 1 -- near-repeat detection (deterministic)
        # -----------------------------------------

        near_repeat_ids = self._find_near_repeats(
            messages,
            current_message
        )
        # -----------------------------------------
# LAYER 2 -- LLM scoring only when needed
# -----------------------------------------

# If every USER message has already been resolved
# deterministically as a near-repeat, there is no
# reason to spend an LLM call.

        user_message_ids = {
            str(message.message_id)
            for message in messages
            if (message.role or "").lower() == "user"
}

        if user_message_ids and user_message_ids.issubset(
            near_repeat_ids
):
            return [
                ConversationScore(
                    message_id=str(message.message_id),
                    score=1.0 if str(message.message_id) in near_repeat_ids else 0.0,
                    is_high_value=str(message.message_id) in near_repeat_ids,
                    reasoning=(
                        "near-duplicate of current message "
                        "(deterministic match)"
                        if str(message.message_id) in near_repeat_ids
                        else "deterministic conversation relevance"
            )
        )
                for message in messages
    ]

        prompt = self._build_prompt(
            messages,
            current_message
)

        result = self.llm_service.generate_structured(
            prompt=prompt,
            temperature=0.0
)





        scores_by_id = {
            str(item.get("message_id")): item
            for item in result.get("scores", [])
        }

        final_scores = []

        for message in messages:
            mid = str(message.message_id)

            # Near-repeat override: bypass the LLM's judgment entirely.
            if mid in near_repeat_ids:
                final_scores.append(
                    ConversationScore(
                        message_id=mid,
                        score=1.0,
                        is_high_value=True,
                        reasoning="near-duplicate of current message (deterministic match)"
                    )
                )
                continue

            item = scores_by_id.get(mid)
            llm_score = float(item["score"]) if item else 0.3
            reasoning = item.get("reasoning", "") if item else ""

            recency = self._recency_score(message.created_at)

            final = max(0.0, min(1.0, (llm_score * 0.75) + (recency * 0.25)))

            final_scores.append(
                ConversationScore(
                    message_id=mid,
                    score=final,
                    is_high_value=(final >= self.HIGH_VALUE_THRESHOLD),
                    reasoning=reasoning
                )
            )

        return final_scores

    # ==========================================
    # NEAR-REPEAT DETECTION -- cheap, no LLM call
    # ==========================================

    def _find_near_repeats(
        self,
        messages: list,
        current_message: str
    ) -> set[str]:

        current_norm = self._normalize(current_message)
        matches = set()

        for message in messages:

            if (message.role or "").lower() != "user":
                # Only compare against previous USER messages --
                # we're detecting "did the user already ask this",
                # not matching against assistant replies.
                continue

            candidate_norm = self._normalize(message.content or "")

            if not candidate_norm:
                continue

            similarity = SequenceMatcher(
                None,
                current_norm,
                candidate_norm
            ).ratio()

            if similarity >= self.NEAR_REPEAT_THRESHOLD:
                matches.add(str(message.message_id))

        return matches

    def _normalize(self, text: str) -> str:
        """
        Strip filler words that inflate/deflate similarity without
        changing meaning -- "bro", "please", "hey" etc. -- so
        "bro explain python functions" and "explain python functions"
        are correctly recognized as near-identical.
        """
        filler_words = {"bro", "please", "hey", "yo", "ira", "pls", "plz"}

        words = text.lower().strip().split()
        cleaned = [w for w in words if w not in filler_words]

        return " ".join(cleaned)

    # ==========================================
    # RECENCY -- deterministic, not a judgment call
    # ==========================================

    def _recency_score(self, created_at) -> float:

        if created_at is None:
            return 0.0

        now = datetime.now(timezone.utc)

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age_seconds = (now - created_at).total_seconds()

        if age_seconds <= 0:
            return 1.0

        hours = age_seconds / 3600
        return max(0.0, min(1.0, 1.0 / (1.0 + hours / 6.0)))

    # ==========================================
    # PROMPT -- for the fuzzy, non-repeat cases
    # ==========================================

    def _build_prompt(self, messages: list, current_message: str) -> str:

        conversation_text = "\n".join(
            f'{{"message_id": "{m.message_id}", "role": "{m.role}", "content": {json.dumps(m.content)}}}'
            for m in messages
        )

        return f"""
You are scoring recent conversation messages for how useful each one
is for understanding the CURRENT user message below.

Judge usefulness the way a thoughtful human assistant would -- not by
matching keywords. Consider things like:
- Does this message explain what "it", "this", "that", "same one",
  or a follow-up like "why?" or "make it better" in the current
  message is referring to?
- Does this message contain a decision, plan, code, or fact the
  current message is building on, modifying, or continuing?
- Is this message just small talk (greetings, thanks, acknowledgments)
  with no bearing on the current message?
- Could this message be safely dropped from context without changing
  how well you could answer the current message?

Score each message from 0.0 (irrelevant, safe to drop) to 1.0
(essential to understanding the current message).

<conversation_history>
{conversation_text}
</conversation_history>

<current_message>
{current_message}
</current_message>

Return ONLY valid JSON, no markdown, no commentary:

{{
  "scores": [
    {{"message_id": "...", "score": 0.0, "reasoning": "one short phrase"}}
  ]
}}

Score every message_id from the conversation history above, in any order.
"""