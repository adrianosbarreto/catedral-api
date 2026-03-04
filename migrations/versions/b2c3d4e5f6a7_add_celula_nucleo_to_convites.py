"""add celula_id and nucleo_id to convites

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-03 23:28:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('convites', schema=None) as batch_op:
        batch_op.add_column(sa.Column('celula_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nucleo_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_convites_celula_id', 'celulas', ['celula_id'], ['id'])
        batch_op.create_foreign_key('fk_convites_nucleo_id', 'nucleos', ['nucleo_id'], ['id'])


def downgrade():
    with op.batch_alter_table('convites', schema=None) as batch_op:
        batch_op.drop_constraint('fk_convites_celula_id', type_='foreignkey')
        batch_op.drop_constraint('fk_convites_nucleo_id', type_='foreignkey')
        batch_op.drop_column('nucleo_id')
        batch_op.drop_column('celula_id')
