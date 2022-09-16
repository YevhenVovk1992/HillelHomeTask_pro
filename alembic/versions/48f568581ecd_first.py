"""first

Revision ID: 48f568581ecd
Revises: 
Create Date: 2022-09-16 15:45:55.352997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48f568581ecd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currency',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.Column('cost_relative_USD', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('act_date', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deposit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('login_user', sa.String(length=50), nullable=False),
    sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('open_date', sa.String(length=50), nullable=False),
    sa.Column('close_date', sa.String(length=50), nullable=True),
    sa.Column('interest_rate', sa.Integer(), nullable=False),
    sa.Column('conditions', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('money_transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user_1', sa.String(length=50), nullable=False),
    sa.Column('id_user_2', sa.String(length=50), nullable=False),
    sa.Column('type_operation', sa.String(length=30), nullable=False),
    sa.Column('spent_currency', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('start_currency', sa.String(length=30), nullable=True),
    sa.Column('end_currency', sa.String(length=30), nullable=True),
    sa.Column('operation_time', sa.String(length=30), nullable=False),
    sa.Column('received_currency', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('commission', sa.Integer(), nullable=True),
    sa.Column('from_bank_account', sa.Integer(), nullable=False),
    sa.Column('on_which_bank_account', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_currency', sa.String(length=50), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('login', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('login')
    )
    op.create_table('bank_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('login_user', sa.String(length=50), nullable=False),
    sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['login_user'], ['user.login'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bank_account')
    op.drop_table('user')
    op.drop_table('rating')
    op.drop_table('money_transaction')
    op.drop_table('deposit')
    op.drop_table('currency')
    # ### end Alembic commands ###
