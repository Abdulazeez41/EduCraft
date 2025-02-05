"""Updated Instructor registration model

Revision ID: 46564e94cd06
Revises: 859bee61b351
Create Date: 2025-02-02 01:39:03.405842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46564e94cd06'
down_revision = '859bee61b351'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instructor_profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('bio', sa.Text(), nullable=False),
    sa.Column('expertise', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('instructor_profiles')
    # ### end Alembic commands ###
