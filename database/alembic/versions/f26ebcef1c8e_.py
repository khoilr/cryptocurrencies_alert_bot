"""empty message

Revision ID: f26ebcef1c8e
Revises: 643312d02128
Create Date: 2023-10-13 22:46:31.998787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f26ebcef1c8e'
down_revision: Union[str, None] = '643312d02128'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('alerts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('params', sa.JSON(), nullable=True),
    sa.Column('condition', sa.String(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('interval', sa.String(), nullable=True),
    sa.Column('klines', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('alerts')
    # ### end Alembic commands ###
