from brain.conversation.conversation_summary_policy import (
    ConversationSummaryPolicy,
)
from brain.conversation.conversation_summary_service import (
    ConversationSummaryService,
)
from brain.conversation.conversation_summary_generator import (
    ConversationSummaryGenerator,
)


class ConversationSummaryOrchestrator:
    """
    Coordinates conversation summarization.

    Responsibilities:

    - decide whether summarization is needed
    - load existing summary
    - obtain messages requiring summarization
    - generate updated summary
    - persist the updated summary

    It does NOT:

    - delete raw messages
    - replace conversation history
    - build the final chat context
    - directly call a model provider
    """

    def __init__(
        self,
        summary_service: ConversationSummaryService,
        summary_generator: ConversationSummaryGenerator,
        policy: ConversationSummaryPolicy,
        conversation_repository,
    ):
        if summary_service is None:
            raise ValueError(
                "Summary service is required."
            )

        if summary_generator is None:
            raise ValueError(
                "Summary generator is required."
            )

        if policy is None:
            raise ValueError(
                "Summary policy is required."
            )

        if conversation_repository is None:
            raise ValueError(
                "Conversation repository is required."
            )

        self.summary_service = summary_service
        self.summary_generator = summary_generator
        self.policy = policy
        self.conversation_repository = (
            conversation_repository
        )

    # =====================================================
    # SUMMARIZE IF NEEDED
    # =====================================================

    def summarize_if_needed(
        self,
        conversation_id: str,
        user_id: int,
    ):
        """
        Generate or update a conversation summary only when
        the configured policy says enough new history exists.

        Returns:
            Summary model when a summary is created or updated.
            None when summarization is not required.
        """

        total_message_count = (
            self.conversation_repository.count_messages(
                user_id=user_id,
                conversation_id=conversation_id,
            )
        )

        existing_summary = (
            self.summary_service.get_summary(
                conversation_id=conversation_id,
                user_id=user_id,
            )
        )

        summarized_message_count = (
            existing_summary.message_count
            if existing_summary is not None
            else 0
        )

        if not self.policy.should_summarize(
            total_message_count=total_message_count,
            summarized_message_count=summarized_message_count,
):
            return None


        summarized_until_message_id = (
            existing_summary.summarized_until_message_id
            if existing_summary is not None
            else 0
        )

        messages = (
            self.conversation_repository.get_messages_after_id(
                user_id=user_id,
                conversation_id=conversation_id,
                message_id=summarized_until_message_id,
            )
        )



        if not messages:
            return None

        previous_summary = (
            existing_summary.summary
            if existing_summary is not None
            else None
        )


        generated_summary = (
            self.summary_generator.generate(
                previous_summary=previous_summary,
                messages=messages,
            )
        )

        last_message = messages[-1]

        if existing_summary is None:
            return self.summary_service.create_summary(
                conversation_id=conversation_id,
                user_id=user_id,
                summary=generated_summary,
                summarized_until_message_id=(
                    last_message.message_id
                ),
                message_count=len(messages),
                version=1,
            )

        return self.summary_service.update_summary(
            summary_model=existing_summary,
            summary=generated_summary,
            summarized_until_message_id=(
                last_message.message_id
            ),
            message_count=(
                existing_summary.message_count
                + len(messages)
            ),
            version=(
                existing_summary.version + 1
            ),
        )