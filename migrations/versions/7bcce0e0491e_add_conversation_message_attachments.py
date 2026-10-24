"""Add attachment metadata to conversation messages."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "7bcce0e0491e"
down_revision: Union[str, Sequence[str], None] = "0adc59ec8c49"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversation_messages",
        sa.Column("attachments", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("conversation_messages", "attachments")
