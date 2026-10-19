"""add google authentication

Revision ID: feb6a4764d37
Revises: 82d63c218e24
Create Date: 2026-09-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "feb6a4764d37"
down_revision: Union[str, Sequence[str], None] = "82d63c218e24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    op.add_column(
        "users",
        sa.Column(
            "google_sub",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_google_sub",
        "users",
        ["google_sub"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_users_google_sub",
        table_name="users",
    )

    op.drop_column(
        "users",
        "google_sub",
    )

    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=False,
    )