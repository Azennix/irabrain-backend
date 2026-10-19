"""add project tasks

Revision ID: 4412d5b1a08e
Revises: fa2dc1f59060
Create Date: 2026-09-25 11:55:50.873110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4412d5b1a08e'
down_revision: Union[str, Sequence[str], None] = 'fa2dc1f59060'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "project_tasks",
        sa.Column("task_id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("task_id"),
    )


def downgrade():
    op.drop_table("project_tasks")