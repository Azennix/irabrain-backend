"""add llm usage table

Revision ID: 3c4ff855f59f
Revises: 5dfedf141d00
Create Date: 2026-10-03 19:00:20.482985

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c4ff855f59f"
down_revision: Union[str, Sequence[str], None] = "5dfedf141d00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "llm_usage",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "request_id",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "provider",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "model",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "input_tokens",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "output_tokens",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "cached_tokens",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "reasoning_tokens",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "total_tokens",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "estimated_cost",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "latency",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "success",
            sa.Boolean(),
            nullable=False,
            default=True,
        ),

        sa.Column(
            "error",
            sa.String(length=2000),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_llm_usage_request_id",
        "llm_usage",
        ["request_id"],
        unique=False,
    )

    op.create_index(
        "ix_llm_usage_user_id",
        "llm_usage",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_llm_usage_user_id",
        table_name="llm_usage",
    )

    op.drop_index(
        "ix_llm_usage_request_id",
        table_name="llm_usage",
    )

    op.drop_table("llm_usage")