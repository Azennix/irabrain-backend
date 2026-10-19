from sqlalchemy.orm import Session

from brain.conversation.conversation_summary_model import (
    ConversationSummaryModel,
)


class ConversationSummaryRepository:

    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session is required.")

        self.db = db

    def get(
        self,
        conversation_id: str,
        user_id: int,
    ) -> ConversationSummaryModel | None:

        return (
            self.db.query(ConversationSummaryModel)
            .filter(
                ConversationSummaryModel.conversation_id
                == conversation_id,
                ConversationSummaryModel.user_id
                == user_id,
            )
            .first()
        )

    def create(
        self,
        conversation_id: str,
        user_id: int,
        summary: str,
        summarized_until_message_id: int,
        message_count: int,
        version: int = 1,
    ) -> ConversationSummaryModel:

        summary_model = ConversationSummaryModel(
            conversation_id=conversation_id,
            user_id=user_id,
            summary=summary,
            summarized_until_message_id=summarized_until_message_id,
            message_count=message_count,
            version=version,
        )

        self.db.add(summary_model)
        self.db.flush()

        return summary_model

    def update(
        self,
        summary_model: ConversationSummaryModel,
        summary: str,
        summarized_until_message_id: int,
        message_count: int,
        version: int,
    ) -> ConversationSummaryModel:

        summary_model.summary = summary
        summary_model.summarized_until_message_id = (
            summarized_until_message_id
        )
        summary_model.message_count = message_count
        summary_model.version = version

        self.db.flush()

        return summary_model