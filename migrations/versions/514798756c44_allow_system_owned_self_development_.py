from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "514798756c44"
down_revision: Union[str, Sequence[str], None] = "a9f59c101976"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "self_development_cycles",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "self_development_cycles",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )