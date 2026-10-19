"""add notes

Revision ID: 94538ae48ab5
Revises: 95c59a96b57a
Create Date: 2026-09-28 01:30:28.369453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '94538ae48ab5'
down_revision: Union[str, Sequence[str], None] = '95c59a96b57a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notes",
        sa.Column("note_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("note_id"),
    )

    op.create_index(
        op.f("ix_notes_user_id"),
        "notes",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_notes_user_id"),
        table_name="notes",
    )

    op.drop_table("notes")