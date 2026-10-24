from brain.conversation.conversation_repository import ConversationRepository
from brain.conversation.conversation_scorer import ConversationScorer


class ConversationService:
    """
    Application service for conversation history.

    Responsibilities:

    - create conversations
    - save user messages
    - save assistant messages
    - retrieve previous conversation
    - retrieve user's conversations
    - score previous messages for relevance

    It does NOT:
    - generate responses
    - perform reasoning
    - select tools
    - build prompts
    """

    def __init__(
        self,
        db,
        scorer: ConversationScorer
    ):
        self.repository = ConversationRepository(db)
        self.scorer = scorer

    # =====================================================
    # CREATE CONVERSATION
    # =====================================================

    def create_conversation(
        self,
        conversation_id: str,
        user_id: int,
        title: str
    ):
        return self.repository.create_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title
        )

    # =====================================================
    # GET CONVERSATION
    # =====================================================

    def get_conversation(
        self,
        conversation_id: str,
        user_id: int
    ):
        return self.repository.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id
        )


        # =====================================================
    # TOUCH CONVERSATION
    # =====================================================

    def touch_conversation(
        self,
        conversation_id: str,
        user_id: int
    ):
        return self.repository.touch_conversation(
            conversation_id=conversation_id,
            user_id=user_id
        )

    # =====================================================
    # GET USER CONVERSATIONS
    # =====================================================

    def get_user_conversations(
        self,
        user_id: int,
        limit: int = 50
    ):
        return self.repository.get_user_conversations(
            user_id=user_id,
            limit=limit
        )

    # =====================================================
    # UPDATE CONVERSATION
    # =====================================================

    def update_conversation(
        self,
        conversation,
        title: str | None = None
    ):
        return self.repository.update_conversation(
            conversation=conversation,
            title=title
        )

    # =====================================================
    # SAVE USER MESSAGE
    # =====================================================

    def save_user_message(
        self,
        user_id: int,
        content: str,
        conversation_id: str | None = None,
        attachments: list[dict] | None = None
    ):
        return self.repository.save(
            user_id=user_id,
            role="user",
            content=content,
            conversation_id=conversation_id,
            attachments=attachments
        )

    # =====================================================
    # SAVE ASSISTANT MESSAGE
    # =====================================================

    def save_assistant_message(
        self,
        user_id: int,
        content: str,
        conversation_id: str | None = None,
        visual_data: dict | None = None
    ):
        return self.repository.save(
            user_id=user_id,
            role="assistant",
            content=content,
            conversation_id=conversation_id,
            visual_data=visual_data
        )

    # =====================================================
    # RECENT CONVERSATION
    # =====================================================

    def get_recent_conversation(
        self,
        user_id: int,
        current_message: str | None = None,
        current_message_id: int | None = None,
        limit: int = 10,
        conversation_id: str | None = None
    ):

        messages = self.repository.get_recent(
            user_id=user_id,
            limit=limit,
            conversation_id=conversation_id
        )

        messages = list(
            reversed(messages)
        )

        # -------------------------------------------------
        # REMOVE CURRENT MESSAGE
        # -------------------------------------------------

        if current_message_id is not None:

            messages = [
                message
                for message in messages
                if message.message_id != current_message_id
            ]

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        elif current_message is not None:

            normalized_current = (
                " ".join(
                    current_message
                    .strip()
                    .lower()
                    .split()
                )
            )

            for index in range(
                len(messages) - 1,
                -1,
                -1
            ):

                message = messages[index]

                normalized_message = (
                    " ".join(
                        (message.content or "")
                        .strip()
                        .lower()
                        .split()
                    )
                )

                if (
                    (message.role or "").lower() == "user"
                    and normalized_message == normalized_current
                ):

                    messages.pop(index)

                    break

        # -------------------------------------------------
        # SCORE HISTORY
        # -------------------------------------------------

        if not messages:

            return []

        scores = self.scorer.score_conversation(
            messages=messages,
            current_message=current_message or ""
        )

        score_by_id = {
            str(score.message_id): score
            for score in scores
        }

        # -------------------------------------------------
        # ATTACH RELEVANCE SCORE
        # -------------------------------------------------

        for message in messages:

            message.relevance_score = (
                score_by_id.get(
                    str(message.message_id)
                )
            )

        return messages

        # =====================================================
    # DELETE CONVERSATION
    # =====================================================

    def delete_conversation(
        self,
        user_id: int,
        conversation_id: str
    ) -> bool:

        return (
            self.repository
            .delete_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )
        )

    # =====================================================
    # FULL CONVERSATION HISTORY
    # =====================================================

    def get_conversation_history(
        self,
        user_id: int,
        limit: int = 50,
        conversation_id: str | None = None
    ):
        """
        Return conversation messages.

        When conversation_id is supplied, only that
        conversation is returned.

        When omitted, existing user-wide history behavior
        is preserved.
        """

        messages = self.repository.get_recent(
            user_id=user_id,
            limit=limit,
            conversation_id=conversation_id
        )



        return list(
            reversed(messages)

        )
    def count_messages(
        self,
        user_id: int,
        conversation_id: str
    ) -> int:

        return self.repository.count_messages(
            user_id=user_id,
            conversation_id=conversation_id
    )
    def commit(self):
        self.repository.commit()
