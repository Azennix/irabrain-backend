"""add conversations

Revision ID: 50c271d01a6c
Revises: 42dc36cbecab
Create Date: 2026-09-20 17:02:54.661509

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "50c271d01a6c"
down_revision: Union[str, Sequence[str], None] = "42dc36cbecab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------
    # 1. CREATE CONVERSATIONS TABLE
    # -------------------------------------------------

    op.create_table(
        "conversations",

        sa.Column(
            "conversation_id",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "conversation_id"
        ),
    )

    op.create_index(
        "ix_conversations_user_id",
        "conversations",
        ["user_id"],
        unique=False,
    )

        # -------------------------------------------------
    # 2. CREATE CONVERSATION MESSAGES TABLE
    # -------------------------------------------------

    op.create_table(
        "conversation_messages",
        sa.Column(
            "message_id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("message_id"),
    )

    op.create_index(
        "ix_conversation_messages_user_id",
        "conversation_messages",
        ["user_id"],
        unique=False,
    )

    # -------------------------------------------------
    # 3. ADD CONVERSATION ID TO MESSAGES
    # -------------------------------------------------

    op.add_column(
        "conversation_messages",
        sa.Column(
            "conversation_id",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_conversation_messages_conversation_id",
        "conversation_messages",
        ["conversation_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop message indexes before dropping their table.
    op.drop_index(
        "ix_conversation_messages_conversation_id",
        table_name="conversation_messages",
    )

    op.drop_index(
        "ix_conversation_messages_user_id",
        table_name="conversation_messages",
    )

    # Drop the messages table.
    op.drop_table("conversation_messages")

    # Drop the conversations index before its table.
    op.drop_index(
        "ix_conversations_user_id",
        table_name="conversations",
    )

    # Drop the conversations table.
    op.drop_table("conversations")