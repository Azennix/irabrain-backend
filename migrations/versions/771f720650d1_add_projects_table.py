"""add projects table

Revision ID: 771f720650d1
Revises: 0b9e65f51e66
Create Date: 2026-09-24 16:21:46.936035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '771f720650d1'
down_revision: Union[str, Sequence[str], None] = '0b9e65f51e66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'projects',
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('project_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('projects')
    # ### end Alembic commands ###
