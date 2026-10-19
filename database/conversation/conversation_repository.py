from datetime import datetime

from sqlalchemy.orm import Session

from brain.conversation.conversation_model import (
    ConversationModel
)
from database.conversation.conversation_message_model import (
    ConversationMessageModel
)


class ConversationRepository:

    def __init__(self, db: Session):

        self.db = db

    # =====================================================
    # CREATE CONVERSATION
    # =====================================================

    def create_conversation(
        self,
        conversation_id: str,
        user_id: int,
        title: str
    ) -> ConversationModel:

        conversation = ConversationModel(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(conversation)

        self.db.flush()

        return conversation

    # =====================================================
    # GET CONVERSATION
    # =====================================================

    def get_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> ConversationModel | None:

        return (
            self.db.query(
                ConversationModel
            )
            .filter(
                ConversationModel.conversation_id
                == conversation_id,
                ConversationModel.user_id
                == user_id
            )
            .first()
        )

    # =====================================================
    # GET USER CONVERSATIONS
    # =====================================================

    def get_user_conversations(
        self,
        user_id: int,
        limit: int = 50
    ) -> list[ConversationModel]:

        return (
            self.db.query(
                ConversationModel
            )
            .filter(
                ConversationModel.user_id == user_id
            )
            .order_by(
                ConversationModel.updated_at.desc()
            )
            .limit(limit)
            .all()
        )

        # =====================================================
    # DELETE CONVERSATION
    # =====================================================

    def delete_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> bool:

        conversation = (
            self.db.query(
                ConversationModel
            )
            .filter(
                ConversationModel.conversation_id
                == conversation_id,
                ConversationModel.user_id
                == user_id
            )
            .first()
        )

        if conversation is None:
            return False

        (
            self.db.query(
                ConversationMessageModel
            )
            .filter(
                ConversationMessageModel.conversation_id
                == conversation_id,
                ConversationMessageModel.user_id
                == user_id
            )
            .delete(
                synchronize_session=False
            )
        )

        self.db.delete(conversation)

        self.db.flush()

        return True

    # =====================================================
    # UPDATE CONVERSATION
    # =====================================================

    def update_conversation(
        self,
        conversation: ConversationModel,
        title: str | None = None
    ) -> ConversationModel:

        if title is not None:
            conversation.title = title

        conversation.updated_at = datetime.utcnow()

        self.db.flush()

        return conversation

    # =====================================================
    # SAVE MESSAGE
    # =====================================================

    def create(
        self,
        user_id: int,
        role: str,
        content: str,
        conversation_id: str | None = None
    ) -> ConversationMessageModel:

        message = ConversationMessageModel(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content
        )

        self.db.add(message)

        self.db.flush()

        return message

    # =====================================================
    # GET RECENT MESSAGES
    # =====================================================

    def get_recent_messages(
        self,
        user_id: int,
        limit: int = 10,
        conversation_id: str | None = None
    ) -> list[ConversationMessageModel]:

        query = (
            self.db.query(
                ConversationMessageModel
            )
            .filter(
                ConversationMessageModel.user_id == user_id
            )
        )

        if conversation_id is not None:

            query = query.filter(
                ConversationMessageModel.conversation_id
                == conversation_id
            )

        messages = (
            query
            .order_by(
                ConversationMessageModel.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return list(
            reversed(messages)
        )

    # =====================================================
    # COMMIT
    # =====================================================

    def commit(self) -> None:

        self.db.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self) -> None:

        self.db.rollback()