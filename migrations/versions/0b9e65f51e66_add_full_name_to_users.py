"""add full name to users

Revision ID: 0b9e65f51e66
Revises: 50c271d01a6c
Create Date: 2026-09-21 01:52:21.752821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b9e65f51e66'
down_revision: Union[str, Sequence[str], None] = '50c271d01a6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "users",
        sa.Column(
            "full_name",
            sa.String(length=255),
            nullable=True
        )
    )


def downgrade() -> None:

    op.drop_column(
        "users",
        "full_name"
    )
