"""agregar_tipos_vehiculo_furgon_camion_otros

Revision ID: 4be64630245c
Revises: 8ec44c2d86d8
"""
from alembic import op
import sqlalchemy as sa


revision = '4be64630245c'
down_revision = '8ec44c2d86d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('ck_vehiculo_tipo', 'vehiculo', type_='check')
    op.create_check_constraint(
        'ck_vehiculo_tipo',
        'vehiculo',
        "tipo IN ('MOTO', 'AUTOMOVIL', 'CAMIONETA', 'FURGON', 'CAMION', 'OTROS')"
    )


def downgrade() -> None:
    op.drop_constraint('ck_vehiculo_tipo', 'vehiculo', type_='check')
    op.create_check_constraint(
        'ck_vehiculo_tipo',
        'vehiculo',
        "tipo IN ('MOTO', 'AUTOMOVIL', 'CAMIONETA')"
    )
