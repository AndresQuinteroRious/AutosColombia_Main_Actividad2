"""Unificar los tipos de vehículo y celda."""
from alembic import op

revision = "tipos_vehiculo_celda"
down_revision = "mensualidad_estado_sin_fechas"
branch_labels = None
depends_on = None

TIPOS = "tipo IN ('AUTOMOVIL', 'MOTOCICLETA')"


def upgrade() -> None:
    op.drop_constraint("ck_vehiculo_tipo", "vehiculo", type_="check")
    for tabla in ("vehiculo", "celda"):
        op.execute(f"""
            UPDATE {tabla}
            SET tipo = CASE
                WHEN upper(btrim(tipo)) IN ('MOTO', 'MOTOCICLETA') THEN 'MOTOCICLETA'
                ELSE 'AUTOMOVIL'
            END
            WHERE tipo NOT IN ('AUTOMOVIL', 'MOTOCICLETA')
        """)
        op.create_check_constraint(f"ck_{tabla}_tipo", tabla, TIPOS)


def downgrade() -> None:
    for tabla in ("vehiculo", "celda"):
        op.drop_constraint(f"ck_{tabla}_tipo", tabla, type_="check")
        op.execute(f"UPDATE {tabla} SET tipo = 'MOTO' WHERE tipo = 'MOTOCICLETA'")
    op.create_check_constraint(
        "ck_vehiculo_tipo",
        "vehiculo",
        "tipo IN ('MOTO', 'AUTOMOVIL', 'CAMIONETA', 'FURGON', 'CAMION', 'OTROS')",
    )
