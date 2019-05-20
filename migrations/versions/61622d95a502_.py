"""empty message

Revision ID: 61622d95a502
Revises: 8d94225a21f3
Create Date: 2019-05-06 10:44:11.579695

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '61622d95a502'
down_revision = '8d94225a21f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('inventory')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('inventory',
    sa.Column('库存编号', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('类型', mysql.ENUM('in', 'out', 'adjust'), nullable=True),
    sa.Column('库存数量', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('物料名称', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('物料ID', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['物料ID'], ['materials.ID'], name='inventory_ibfk_1'),
    sa.PrimaryKeyConstraint('\u5e93\u5b58\u7f16\u53f7'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###