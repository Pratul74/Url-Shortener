"""rename analytics columns

Revision ID: 074295438510
Revises: f057fa72f29a
Create Date: 2026-09-28 18:06:59.035171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '074295438510'
down_revision: Union[str, Sequence[str], None] = 'f057fa72f29a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "analytics",
        "countries",
        new_column_name="country"
    )

    op.alter_column(
        "analytics",
        "cities",
        new_column_name="city"
    )

    op.alter_column(
        "analytics",
        "browsers",
        new_column_name="browser"
    )

    op.alter_column(
        "analytics",
        "devices",
        new_column_name="device"
    )


def downgrade():
    op.alter_column(
        "analytics",
        "country",
        new_column_name="countries"
    )

    op.alter_column(
        "analytics",
        "city",
        new_column_name="cities"
    )

    op.alter_column(
        "analytics",
        "browser",
        new_column_name="browsers"
    )

    op.alter_column(
        "analytics",
        "device",
        new_column_name="devices"
    )
