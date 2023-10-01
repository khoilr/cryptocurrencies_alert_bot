"""create tables

Revision ID: 07d8c7628b8f
Revises: 51afe2156e75
Create Date: 2023-09-30 18:20:23.320872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07d8c7628b8f'
down_revision: Union[str, None] = '51afe2156e75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
