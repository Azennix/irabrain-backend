"""add goal to project tasks

Revision ID: add3b194fc56
Revises: 4412d5b1a08e
Create Date: 2026-09-25 21:05:14.767975

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add3b194fc56'
down_revision: Union[str, Sequence[str], None] = '4412d5b1a08e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "project_tasks",
        sa.Column(
            "goal_id",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "project_tasks",
        "goal_id",
    )