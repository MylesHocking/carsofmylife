"""Added is_generic_model to car_data

Revision ID: ea22964ac43f
Revises: 468080b0267c
Create Date: 2023-10-31 11:52:30.867096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea22964ac43f'
down_revision = '468080b0267c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('car_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_generic_model', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('car_data', schema=None) as batch_op:
        batch_op.drop_column('is_generic_model')

    # ### end Alembic commands ###
