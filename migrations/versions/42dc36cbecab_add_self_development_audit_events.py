"""add self development audit events

Revision ID: 42dc36cbecab
Revises: 514798756c44
Create Date: 2026-09-19 23:18:02.837154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42dc36cbecab'
down_revision: Union[str, Sequence[str], None] = '514798756c44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "self_development_audit_events",
        sa.Column("event_id", sa.String(length=100), nullable=False),
        sa.Column("cycle_id", sa.String(length=100), nullable=False),
        sa.Column("system_id", sa.String(length=100), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("stage", sa.String(length=50), nullable=True),
        sa.Column("outcome", sa.String(length=50), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )

    op.create_index(
        "ix_self_development_audit_events_cycle_id",
        "self_development_audit_events",
        ["cycle_id"],
    )

    op.create_index(
        "ix_self_development_audit_events_system_id",
        "self_development_audit_events",
        ["system_id"],
    )

    op.create_index(
        "ix_self_development_audit_events_user_id",
        "self_development_audit_events",
        ["user_id"],
    )

    op.create_index(
        "ix_self_development_audit_events_event_type",
        "self_development_audit_events",
        ["event_type"],
    )


def downgrade():
    op.drop_index(
        "ix_self_development_audit_events_event_type",
        table_name="self_development_audit_events",
    )
    op.drop_index(
        "ix_self_development_audit_events_user_id",
        table_name="self_development_audit_events",
    )
    op.drop_index(
        "ix_self_development_audit_events_system_id",
        table_name="self_development_audit_events",
    )
    op.drop_index(
        "ix_self_development_audit_events_cycle_id",
        table_name="self_development_audit_events",
    )
    op.drop_table("self_development_audit_events")
