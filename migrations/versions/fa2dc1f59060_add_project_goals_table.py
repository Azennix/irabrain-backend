"""add project goals table

Revision ID: fa2dc1f59060
Revises: 771f720650d1
Create Date: 2026-09-24 17:01:12.243811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fa2dc1f59060'
down_revision: Union[str, Sequence[str], None] = '771f720650d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "project_goals",
        sa.Column("goal_id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("goal_id"),
    )
def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("project_goals")