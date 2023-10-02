"""empty message

Revision ID: 5c80792d82f2
Revises: 
Create Date: 2023-10-01 22:36:17.398401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c80792d82f2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cryptos',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('symbol', sa.String(length=20), nullable=False),
    sa.Column('base_asset', sa.String(length=10), nullable=False),
    sa.Column('quote_asset', sa.String(length=10), nullable=False),
    sa.Column('updated_at', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cryptos_base_asset'), 'cryptos', ['base_asset'], unique=False)
    op.create_index(op.f('ix_cryptos_count'), 'cryptos', ['count'], unique=False)
    op.create_index(op.f('ix_cryptos_id'), 'cryptos', ['id'], unique=False)
    op.create_index(op.f('ix_cryptos_quote_asset'), 'cryptos', ['quote_asset'], unique=False)
    op.create_index(op.f('ix_cryptos_symbol'), 'cryptos', ['symbol'], unique=False)
    op.create_index(op.f('ix_cryptos_updated_at'), 'cryptos', ['updated_at'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_cryptos_updated_at'), table_name='cryptos')
    op.drop_index(op.f('ix_cryptos_symbol'), table_name='cryptos')
    op.drop_index(op.f('ix_cryptos_quote_asset'), table_name='cryptos')
    op.drop_index(op.f('ix_cryptos_id'), table_name='cryptos')
    op.drop_index(op.f('ix_cryptos_count'), table_name='cryptos')
    op.drop_index(op.f('ix_cryptos_base_asset'), table_name='cryptos')
    op.drop_table('cryptos')
    # ### end Alembic commands ###
