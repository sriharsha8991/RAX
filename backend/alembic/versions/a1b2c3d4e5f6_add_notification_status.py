"""add notification_status to candidates

Revision ID: a1b2c3d4e5f6
Revises: 4c24c57b118b
Create Date: 2026-04-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "4c24c57b118b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    notificationstatus = postgresql.ENUM(
        "not_sent", "shortlisted", "rejected",
        name="notificationstatus", create_type=False,
    )
    notificationstatus.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "candidates",
        sa.Column(
            "notification_status",
            notificationstatus,
            nullable=False,
            server_default="not_sent",
        ),
    )


def downgrade() -> None:
    op.drop_column("candidates", "notification_status")
    op.execute("DROP TYPE IF EXISTS notificationstatus")
