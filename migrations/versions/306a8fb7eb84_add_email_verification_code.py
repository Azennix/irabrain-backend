"""add email verification code

Revision ID: 306a8fb7eb84
Revises: a5ed7c3b6da2
Create Date: 2026-09-12 14:00:44.888792
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "306a8fb7eb84"
down_revision: Union[str, Sequence[str], None] = "a5ed7c3b6da2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Columns were already added by the preceding migration."""
    pass


def downgrade() -> None:
    """The preceding migration owns these columns."""
    pass