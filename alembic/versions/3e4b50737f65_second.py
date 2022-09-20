"""Second

Revision ID: 3e4b50737f65
Revises: 48f568581ecd
Create Date: 2022-09-16 17:22:38.156442

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e4b50737f65'
down_revision = '48f568581ecd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('queue_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid_money_transaction', sa.String(), nullable=False),
    sa.Column('operation_status', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid_money_transaction')
    )
    op.add_column('money_transaction', sa.Column('uuid_money_transaction', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'money_transaction', ['uuid_money_transaction'])
    op.create_foreign_key(None, 'money_transaction', 'queue_status', ['uuid_money_transaction'], ['uuid_money_transaction'])
    op.drop_column('money_transaction', 'status')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('money_transaction', sa.Column('status', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'money_transaction', type_='foreignkey')
    op.drop_constraint(None, 'money_transaction', type_='unique')
    op.drop_column('money_transaction', 'uuid_money_transaction')
    op.drop_table('queue_status')
    # ### end Alembic commands ###