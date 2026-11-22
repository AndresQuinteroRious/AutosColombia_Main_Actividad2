"""Asociar pagos con vehículos registrados."""
import sqlalchemy as sa
from alembic import op

revision = "pago_vehiculo"
down_revision = "reparar_columnas_usuario"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pago", sa.Column("vehiculo_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fk_pago_vehiculo", "pago", "vehiculo", ["vehiculo_id"], ["id"], ondelete="RESTRICT"
    )
    op.create_index("ix_pago_vehiculo_id", "pago", ["vehiculo_id"])


def downgrade() -> None:
    op.drop_index("ix_pago_vehiculo_id", table_name="pago")
    op.drop_constraint("fk_pago_vehiculo", "pago", type_="foreignkey")
    op.drop_column("pago", "vehiculo_id")
