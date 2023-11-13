"""empty message

Revision ID: 468080b0267c
Revises: a90acb937478
Create Date: 2023-10-30 20:06:32.735410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '468080b0267c'
down_revision = 'a90acb937478'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add the new column as nullable
    op.add_column('users', sa.Column('happy2show', sa.Boolean(), nullable=True))

    # Step 2: Populate the new column with default values
    op.execute("UPDATE users SET happy2show = true")  # or false, depending on your default value

    # Step 3: Alter the column to be NOT NULL
    op.alter_column('users', 'happy2show', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'happy2show')

    # ### end Alembic commands ###