"""Reparar bases cuya revisión de turnos figura aplicada pero faltan sus columnas."""
from alembic import op

revision = "reparar_columnas_usuario"
down_revision = "novedad_estancia"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IF NOT EXISTS también permite revisar exactamente este SQL en modo offline.
    for nombre, tipo, valor in (
        ("turno", "TEXT", "'MAÑANA'"),
        ("horas_semana", "INTEGER", "42"),
        ("ausentismo_horas", "INTEGER", "0"),
    ):
        op.execute(f"ALTER TABLE usuario ADD COLUMN IF NOT EXISTS {nombre} {tipo} NOT NULL DEFAULT {valor}")
    for nombre, condicion in (
        ("ck_usuario_turno_valido", "turno IN ('MAÑANA', 'TARDE', 'NOCHE', 'RESPALDO')"),
        ("ck_usuario_horas_semana_valida", "horas_semana BETWEEN 1 AND 84"),
        ("ck_usuario_ausentismo_horas_valida", "ausentismo_horas BETWEEN 0 AND 84"),
    ):
        op.execute(f"""DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint
                WHERE conrelid = 'usuario'::regclass AND conname = '{nombre}') THEN
                ALTER TABLE usuario ADD CONSTRAINT {nombre} CHECK ({condicion});
            END IF;
        END $$""")
    for nombre in ("turno", "horas_semana", "ausentismo_horas"):
        op.execute(f"ALTER TABLE usuario ALTER COLUMN {nombre} DROP DEFAULT")


def downgrade() -> None:
    # Reparación de una revisión anterior: conservar columnas y datos que ya le pertenecen.
    pass
