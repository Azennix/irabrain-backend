class ConversationSummaryGenerator:
    """
    Generates a compact, structured summary of a conversation.

    The generator is responsible only for converting conversation
    content into a summary.

    It does NOT:

    - store summaries
    - decide when summarization should happen
    - retrieve conversation messages
    - replace raw conversation history
    """

    def __init__(self, llm_service):
        if llm_service is None:
            raise ValueError(
                "LLM service is required."
            )

        self.llm_service = llm_service

    def generate(
        self,
        previous_summary: str | None,
        messages,
    ) -> str:

        if not messages:
            raise ValueError(
                "Messages are required to generate a summary."
            )

        conversation_text = "\n".join(
            f"{message.role.upper()}: {message.content}"
            for message in messages
        )

        previous_summary_text = (
            previous_summary.strip()
            if previous_summary
            else "No previous summary exists."
        )

        prompt = f"""
You are the long-term conversation summarization system
for IRABRAIN.

Your job is to create a compact, high-value summary that
preserves the information required to continue the conversation
intelligently later.

IMPORTANT:
- Raw conversation messages remain the source of truth.
- This summary is compressed context only.
- Do not invent information.
- Do not remove important technical or user-specific context.
- Do not include greetings, filler, or repetitive conversation.
- Do not summarize irrelevant small talk.
- Preserve facts and decisions accurately.

The summary should preserve, when present:

1. User goals
2. Important decisions
3. Technical/project state
4. Current task
5. Requirements and constraints
6. User preferences relevant to the conversation
7. Important conclusions
8. Unresolved questions
9. Pending work / next steps
10. Important errors, fixes, or architectural decisions

Previous summary:
<previous_summary>
{previous_summary_text}
</previous_summary>

New conversation messages:
<messages>
{conversation_text}
</messages>

Create an updated summary that combines the previous summary
with the new information.

Return ONLY valid JSON:

{{
    "summary": "..."
}}
"""

        result = self.llm_service.generate_structured(
            prompt=prompt,
            temperature=0.2,
        )

        summary = result.get("summary")

        if not isinstance(summary, str):
            raise ValueError(
                "LLM did not return a valid conversation summary."
            )

        summary = summary.strip()

        if not summary:
            raise ValueError(
                "Generated conversation summary is empty."
            )

        return summary