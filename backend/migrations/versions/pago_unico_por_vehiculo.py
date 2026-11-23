"""Conservar un único pago por vehículo, identificado por su placa única."""
from alembic import op

revision = "pago_unico_por_vehiculo"
down_revision = "tarifas_pago"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("LOCK TABLE pago IN ACCESS EXCLUSIVE MODE")
    op.execute("""
        WITH ordenados AS (
            SELECT id, row_number() OVER (PARTITION BY vehiculo_id ORDER BY fecha DESC, id DESC) AS fila
            FROM pago
            WHERE vehiculo_id IS NOT NULL
        )
        DELETE FROM pago USING ordenados
        WHERE pago.id = ordenados.id AND ordenados.fila > 1
    """)
    op.create_unique_constraint("uq_pago_vehiculo", "pago", ["vehiculo_id"])


def downgrade() -> None:
    # Quitar la restricción no restaura los pagos anteriores eliminados.
    op.drop_constraint("uq_pago_vehiculo", "pago", type_="unique")
