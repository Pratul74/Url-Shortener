"""add an index for URL owner lookups

Revision ID: b6e2a9f74c10
Revises: 5b367ce767f1
Create Date: 2026-11-13 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "b6e2a9f74c10"
down_revision: Union[str, Sequence[str], None] = "5b367ce767f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f("ix_urls_user_id"), "urls", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_urls_user_id"), table_name="urls")
