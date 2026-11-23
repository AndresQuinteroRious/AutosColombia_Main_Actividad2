"""Desactivar las mensualidades sin fechas."""
from alembic import op

revision = "mensualidad_estado_sin_fechas"
down_revision = "mensualidad_fechas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION desactivar_mensualidad_sin_fechas() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.fecha_inicio IS NULL THEN
                NEW.estado := 'desactivado';
            END IF;
            RETURN NEW;
        END;
        $$
    """)
    # fecha_final es generada y queda nula cuando fecha_inicio es nula.
    op.execute("""
        CREATE TRIGGER desactivar_mensualidad_sin_fechas
        BEFORE INSERT OR UPDATE OF fecha_inicio, estado ON mensualidad
        FOR EACH ROW EXECUTE FUNCTION desactivar_mensualidad_sin_fechas()
    """)
    op.execute("""
        UPDATE mensualidad SET estado = 'desactivado'
        WHERE fecha_inicio IS NULL AND estado <> 'desactivado'
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER desactivar_mensualidad_sin_fechas ON mensualidad")
    op.execute("DROP FUNCTION desactivar_mensualidad_sin_fechas()")
