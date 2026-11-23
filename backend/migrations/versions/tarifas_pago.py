"""Guardar las tarifas vigentes de pagos."""
import sqlalchemy as sa
from alembic import op

revision = "tarifas_pago"
down_revision = "activar_mensualidad_al_pagar"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tarifas = op.create_table(
        "tarifa_pago",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("automovil", sa.Numeric(10, 2), nullable=False),
        sa.Column("motocicleta", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_tarifa_pago_configuracion_unica"),
        sa.CheckConstraint(
            "automovil > 0 AND motocicleta > 0", name="ck_tarifa_pago_valores_positivos",
        ),
    )
    op.bulk_insert(tarifas, [{"id": 1, "automovil": 250000, "motocicleta": 125000}])


def downgrade() -> None:
    op.drop_table("tarifa_pago")
