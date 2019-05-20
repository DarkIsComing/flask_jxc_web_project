"""empty message

Revision ID: b34bc7e14e6a
Revises: 745ece127f2c
Create Date: 2019-04-27 09:29:22.823470

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b34bc7e14e6a'
down_revision = '745ece127f2c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('material_detail',
    sa.Column('编号', sa.Integer(), nullable=False),
    sa.Column('物料ID', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['物料ID'], ['materials.ID'], ),
    sa.PrimaryKeyConstraint('编号')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('material_detail')
    # ### end Alembic commands ###
