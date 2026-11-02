"""agregar_direccion_a_operador

Revision ID: agregar_direccion_a_operador
Revises: 68a8a3380d1d
"""
from alembic import op
import sqlalchemy as sa


revision = 'agregar_direccion_a_operador'
down_revision = '68a8a3380d1d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('operador', sa.Column('direccion', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('operador', 'direccion')
