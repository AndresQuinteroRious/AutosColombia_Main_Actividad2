"""agregar_celda_id_a_vehiculo

Revision ID: 8ec44c2d86d8
Revises: 68a8a3380d1d
"""
from alembic import op
import sqlalchemy as sa


revision = '8ec44c2d86d8'
down_revision = '68a8a3380d1d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'vehiculo',
        sa.Column('celda_id', sa.BigInteger(), nullable=True)
    )
    op.create_foreign_key(
        'fk_vehiculo_celda',
        'vehiculo', 'celda',
        ['celda_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_vehiculo_celda', 'vehiculo', type_='foreignkey')
    op.drop_column('vehiculo', 'celda_id')
