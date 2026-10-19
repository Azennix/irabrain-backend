"""repair memory schema and subscription uniqueness

Revision ID: 87b0cfdd4d46
Revises: 7d93938e7c14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "87b0cfdd4d46"
down_revision: Union[str, Sequence[str], None] = "7d93938e7c14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the missing memories table.
    op.create_table(
        "memories",
        sa.Column("memory_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("association_embedding", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("memory_id"),
        sa.UniqueConstraint(
            "user_id",
            "category",
            "key",
            name="uq_memory_user_category_key",
        ),
    )

    # Enforce one subscription record per user.
    op.create_unique_constraint(
        "uq_subscriptions_user_id",
        "subscriptions",
        ["user_id"],
    )


def downgrade() -> None:
    # Remove the subscription uniqueness constraint.
    op.drop_constraint(
        "uq_subscriptions_user_id",
        "subscriptions",
        type_="unique",
    )

    # Remove the table created by this migration.
    op.drop_table("memories")