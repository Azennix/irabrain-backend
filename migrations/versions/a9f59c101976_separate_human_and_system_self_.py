"""separate human and system self development identities

Revision ID: <a9f59c101976>
Revises: 2beb51a141d1
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a9f59c101976"
down_revision: Union[str, Sequence[str], None] = "2beb51a141d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "system_identities",

        sa.Column(
            "system_id",
            sa.String(length=100),
            primary_key=True,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
            unique=True,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO system_identities
            (
                system_id,
                name,
                is_active,
                created_at,
                updated_at
            )
            VALUES
            (
                'IRABRAIN',
                'IRABRAIN Autonomous Self-Development',
                TRUE,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """
        )
    )

    op.add_column(
        "self_development_cycles",
        sa.Column(
            "system_id",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_self_development_cycles_system_id",
        "self_development_cycles",
        ["system_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_self_development_cycles_system_id",
        "self_development_cycles",
        "system_identities",
        ["system_id"],
        ["system_id"],
    )


def downgrade() -> None:

    op.drop_constraint(
        "fk_self_development_cycles_system_id",
        "self_development_cycles",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_self_development_cycles_system_id",
        table_name="self_development_cycles",
    )

    op.drop_column(
        "self_development_cycles",
        "system_id",
    )

    op.drop_table("system_identities")