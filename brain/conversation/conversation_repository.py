from datetime import datetime

from sqlalchemy.orm import Session

from brain.conversation.conversation_model import ConversationModel
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
            self.db.query(ConversationModel)
            .filter(
                ConversationModel.conversation_id == conversation_id,
                ConversationModel.user_id == user_id
            )
            .first()
        )

        # =====================================================
    # TOUCH CONVERSATION
    # =====================================================

    def touch_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> ConversationModel | None:

        conversation = (
            self.db.query(ConversationModel)
            .filter(
                ConversationModel.conversation_id == conversation_id,
                ConversationModel.user_id == user_id
            )
            .first()
        )

        if conversation is None:
            return None

        conversation.updated_at = datetime.utcnow()

        self.db.flush()

        return conversation

    # =====================================================
    # GET USER CONVERSATIONS
    # =====================================================

    def get_user_conversations(
        self,
        user_id: int,
        limit: int = 50
    ) -> list[ConversationModel]:

        return (
            self.db.query(ConversationModel)
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

        # Delete messages belonging to this conversation
        # and this authenticated user.
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

        # Delete the conversation itself.
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

    def save(
        self,
        user_id: int,
        role: str,
        content: str,
        conversation_id: str | None = None,
        visual_data: dict | list[dict] | None = None,
        attachments: list[dict] | None = None
    ):
        # Verify ownership before attaching a message
        # to an existing conversation.
        if conversation_id is not None:
            conversation = (
                self.db.query(ConversationModel)
                .filter(
                    ConversationModel.conversation_id == conversation_id,
                    ConversationModel.user_id == user_id
                )
                .first()
            )

            if conversation is None:
                raise ValueError("Conversation not found.")

        message = ConversationMessageModel(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            visual_data=visual_data,
            attachments=attachments or None
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    # =====================================================
    # =====================================================
    # UPDATE ASSISTANT MESSAGE VISUAL
    # =====================================================

    def update_assistant_visual(
        self,
        *,
        user_id: int,
        message_id: int,
        visual_data: dict | list[dict],
    ):
        message = (
            self.db.query(ConversationMessageModel)
            .filter(
                ConversationMessageModel.message_id == message_id,
                ConversationMessageModel.user_id == user_id,
                ConversationMessageModel.role == "assistant",
            )
            .first()
        )

        if message is None:
            return False

        message.visual_data = visual_data
        self.db.commit()
        self.db.refresh(message)

        return True
    # GET RECENT MESSAGES
    # =====================================================

    def get_recent(
        self,
        user_id: int,
        limit: int = 10,
        conversation_id: str | None = None
    ):
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

        return (
            query
            .order_by(
                ConversationMessageModel.created_at.desc()
            )
            .limit(limit)
            .all()
        )








        # =====================================================
    # GET MESSAGES AFTER SUMMARY BOUNDARY
    # =====================================================

    def get_messages_after_id(
        self,
        user_id: int,
        conversation_id: str,
        message_id: int
    ):
        return (
            self.db.query(
                ConversationMessageModel
            )
            .filter(
                ConversationMessageModel.user_id == user_id,
                ConversationMessageModel.conversation_id
                == conversation_id,
                ConversationMessageModel.message_id
                > message_id
            )
            .order_by(
                ConversationMessageModel.message_id.asc()
            )
            .all()
        )

    def count_messages(
        self,
        user_id: int,
        conversation_id: str
    ) -> int:

        return (
            self.db.query(
                 ConversationMessageModel
        )
            .filter(
                ConversationMessageModel.user_id == user_id,
                ConversationMessageModel.conversation_id == conversation_id
        )
            .count()
    )
    def commit(self):
        self.db.commit()
