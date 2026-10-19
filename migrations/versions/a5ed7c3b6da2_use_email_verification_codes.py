"""use email verification codes

Revision ID: a5ed7c3b6da2
Revises: cc7149a22291
Create Date: 2026-09-12 13:44:18.673126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5ed7c3b6da2'
down_revision: Union[str, Sequence[str], None] = 'cc7149a22291'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "email_verification_code_hash",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "email_verification_code_expires_at",
            sa.DateTime(),
            nullable=True,
        ),
    )



def downgrade() -> None:
    op.drop_column(
        "users",
        "email_verification_code_expires_at",
    )

    op.drop_column(
        "users",
        "email_verification_code_hash",
    )
