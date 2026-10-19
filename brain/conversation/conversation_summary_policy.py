class ConversationSummaryPolicy:
    """
    Deterministic policy for deciding when a conversation
    should be summarized.

    V1 intentionally uses simple message-count boundaries.

    It does NOT:
    - generate summaries
    - call an LLM
    - modify conversation data
    """

    def __init__(
        self,
        minimum_messages: int = 20,
        messages_per_summary: int = 10,
    ):
        if minimum_messages <= 0:
            raise ValueError(
                "minimum_messages must be greater than zero."
            )

        if messages_per_summary <= 0:
            raise ValueError(
                "messages_per_summary must be greater than zero."
            )

        self.minimum_messages = minimum_messages
        self.messages_per_summary = messages_per_summary

    def should_summarize(
        self,
        total_message_count: int,
        summarized_message_count: int = 0,
    ) -> bool:
        """
        Determine whether enough conversation history exists
        to justify generating/updating a summary.
        """

        if total_message_count < self.minimum_messages:
            return False

        if summarized_message_count < 0:
            raise ValueError(
                "summarized_message_count cannot be negative."
            )

        unsummarized_count = (
            total_message_count
            - summarized_message_count
        )

        return (
            unsummarized_count
            >= self.messages_per_summary
        )