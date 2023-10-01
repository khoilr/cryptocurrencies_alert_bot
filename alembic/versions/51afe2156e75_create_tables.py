"""create tables

Revision ID: 51afe2156e75
Revises: 02eb11d472f4
Create Date: 2023-09-30 18:08:06.353279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51afe2156e75'
down_revision: Union[str, None] = '02eb11d472f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
