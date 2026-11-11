"""add response blocks to conversation messages

Revision ID: f8a9a5652178
Revises: 7bcce0e0491e
Create Date: 2026-11-11 23:33:07.749585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a9a5652178'
down_revision: Union[str, Sequence[str], None] = '7bcce0e0491e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.add_column(
        "conversation_messages",
        sa.Column(
            "response_blocks",
            sa.JSON(),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column(
        "conversation_messages",
        "response_blocks"
    )
