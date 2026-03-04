"""add performance indexes

Revision ID: a1b2c3d4e5f6
Revises: 37571d4d8945
Create Date: 2026-03-03 22:47:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = ('37571d4d8945', '02801ab9de76')
branch_labels = None
depends_on = None


def upgrade():
    # ---- papeis_membros ----
    # Usado em JOINs de filtro por role (a query mais lenta)
    op.create_index('ix_papeis_membros_membro_id', 'papeis_membros', ['membro_id'])
    op.create_index('ix_papeis_membros_role_id', 'papeis_membros', ['role_id'])
    op.create_index('ix_papeis_membros_papel', 'papeis_membros', ['papel'])

    # ---- membros ----
    # Filtros mais comuns: ativo, ide_id, lider_id, supervisor_id, nome (LIKE)
    op.create_index('ix_membros_ativo', 'membros', ['ativo'])
    op.create_index('ix_membros_ide_id', 'membros', ['ide_id'])
    op.create_index('ix_membros_lider_id', 'membros', ['lider_id'])
    op.create_index('ix_membros_supervisor_id', 'membros', ['supervisor_id'])
    # Index parcial: membros ativos (mais consultados)
    op.create_index('ix_membros_ativo_ide', 'membros', ['ativo', 'ide_id'])

    # ---- celulas ----
    op.create_index('ix_celulas_ativo', 'celulas', ['ativo'])
    op.create_index('ix_celulas_lider_id', 'celulas', ['lider_id'])
    op.create_index('ix_celulas_supervisor_id', 'celulas', ['supervisor_id'])
    op.create_index('ix_celulas_ide_id', 'celulas', ['ide_id'])


def downgrade():
    # papeis_membros
    op.drop_index('ix_papeis_membros_membro_id', table_name='papeis_membros')
    op.drop_index('ix_papeis_membros_role_id', table_name='papeis_membros')
    op.drop_index('ix_papeis_membros_papel', table_name='papeis_membros')

    # membros
    op.drop_index('ix_membros_ativo', table_name='membros')
    op.drop_index('ix_membros_ide_id', table_name='membros')
    op.drop_index('ix_membros_lider_id', table_name='membros')
    op.drop_index('ix_membros_supervisor_id', table_name='membros')
    op.drop_index('ix_membros_ativo_ide', table_name='membros')

    # celulas
    op.drop_index('ix_celulas_ativo', table_name='celulas')
    op.drop_index('ix_celulas_lider_id', table_name='celulas')
    op.drop_index('ix_celulas_supervisor_id', table_name='celulas')
    op.drop_index('ix_celulas_ide_id', table_name='celulas')
