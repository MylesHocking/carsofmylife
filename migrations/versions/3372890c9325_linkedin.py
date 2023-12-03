"""LinkedIN

Revision ID: 3372890c9325
Revises: 7318f9e4a0a1
Create Date: 2023-12-01 14:41:55.643390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3372890c9325'
down_revision = '7318f9e4a0a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('linkedin_sub', sa.String(length=120), nullable=True))
        batch_op.create_unique_constraint(None, ['linkedin_sub'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('linkedin_sub')

    # ### end Alembic commands ###