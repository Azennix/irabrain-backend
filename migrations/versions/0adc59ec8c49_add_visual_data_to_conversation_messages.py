"""Add visual data to conversation messages."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0adc59ec8c49"
down_revision: Union[str, Sequence[str], None] = "d67c25a47c00"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "conversation_messages",
        sa.Column("visual_data", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("conversation_messages", "visual_data")
