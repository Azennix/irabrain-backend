from brain.conversation.conversation_summary_repository import (
    ConversationSummaryRepository,
)


class ConversationSummaryService:
    """
    Application service for conversation summaries.

    Responsibilities:

    - retrieve an existing conversation summary
    - create a summary
    - update an existing summary
    - track the message boundary covered by the summary

    It does NOT:

    - generate LLM responses
    - decide when summarization should happen
    - retrieve conversation context
    - replace raw conversation messages
    """

    def __init__(
        self,
        db,
    ):
        if db is None:
            raise ValueError("Database session is required.")

        self.repository = ConversationSummaryRepository(db)

    # =====================================================
    # GET SUMMARY
    # =====================================================

    def get_summary(
        self,
        conversation_id: str,
        user_id: int,
    ):
        return self.repository.get(
            conversation_id=conversation_id,
            user_id=user_id,
        )

    # =====================================================
    # CREATE SUMMARY
    # =====================================================

    def create_summary(
        self,
        conversation_id: str,
        user_id: int,
        summary: str,
        summarized_until_message_id: int,
        message_count: int,
        version: int = 1,
    ):
        if not summary or not summary.strip():
            raise ValueError("Summary cannot be empty.")

        if summarized_until_message_id <= 0:
            raise ValueError(
                "Summarized message ID must be greater than zero."
            )

        if message_count < 0:
            raise ValueError(
                "Message count cannot be negative."
            )

        return self.repository.create(
            conversation_id=conversation_id,
            user_id=user_id,
            summary=summary.strip(),
            summarized_until_message_id=(
                summarized_until_message_id
            ),
            message_count=message_count,
            version=version,
        )

    # =====================================================
    # UPDATE SUMMARY
    # =====================================================

    def update_summary(
        self,
        summary_model,
        summary: str,
        summarized_until_message_id: int,
        message_count: int,
        version: int,
    ):
        if summary_model is None:
            raise ValueError(
                "Summary model is required."
            )

        if not summary or not summary.strip():
            raise ValueError("Summary cannot be empty.")

        if summarized_until_message_id <= 0:
            raise ValueError(
                "Summarized message ID must be greater than zero."
            )

        if message_count < 0:
            raise ValueError(
                "Message count cannot be negative."
            )

        if version <= 0:
            raise ValueError(
                "Summary version must be greater than zero."
            )

        return self.repository.update(
            summary_model=summary_model,
            summary=summary.strip(),
            summarized_until_message_id=(
                summarized_until_message_id
            ),
            message_count=message_count,
            version=version,
        )