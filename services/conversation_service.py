from database.conversation.conversation_repository import (
    ConversationRepository
)


class ConversationService:

    def __init__(
        self,
        conversation_repository: ConversationRepository
    ):

        self.conversation_repository = (
            conversation_repository
        )

    # =====================================================
    # SAVE USER MESSAGE
    # =====================================================

    def save_user_message(
        self,
        user_id: int,
        content: str
    ):

        return self.conversation_repository.create(
            user_id=user_id,
            role="user",
            content=content
        )

    # =====================================================
    # SAVE ASSISTANT MESSAGE
    # =====================================================

    def save_assistant_message(
        self,
        user_id: int,
        content: str
    ):

        return self.conversation_repository.create(
            user_id=user_id,
            role="assistant",
            content=content
        )

    # =====================================================
    # GET RECENT CONVERSATION
    # =====================================================

    def get_recent_conversation(
        self,
        user_id: int,
        limit: int = 10
    ):

        return (
            self.conversation_repository
            .get_recent_messages(
                user_id=user_id,
                limit=limit
            )
        )

    # =====================================================
    # COMMIT
    # =====================================================

    def commit(self) -> None:

        self.conversation_repository.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self) -> None:

        self.conversation_repository.rollback()