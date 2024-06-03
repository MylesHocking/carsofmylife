"""Add anonymous user support

Revision ID: 3a826874645a
Revises: 4693e2eaa2df
Create Date: 2024-05-28 14:20:07.856282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a826874645a'
down_revision = '4693e2eaa2df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_anonymous', sa.Boolean(), nullable=True))
        batch_op.alter_column('firstname',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('lastname',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('lastname',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('firstname',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.drop_column('is_anonymous')

    # ### end Alembic commands ###
