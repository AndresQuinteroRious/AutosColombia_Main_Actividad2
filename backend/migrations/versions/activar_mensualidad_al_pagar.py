"""Activar la mensualidad de un vehículo al registrar un pago."""
from alembic import op

revision = "activar_mensualidad_al_pagar"
down_revision = "tipos_vehiculo_celda"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION activar_mensualidad_desde_pago() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            UPDATE mensualidad
            SET estado = 'activo'
            WHERE id_mensualidad = (
                SELECT id_mensualidad
                FROM mensualidad
                WHERE id_vehiculo = NEW.vehiculo_id
                ORDER BY id_mensualidad DESC
                LIMIT 1
            )
            AND fecha_inicio IS NOT NULL;
            RETURN NULL;
        END;
        $$
    """)
    # PostgreSQL ejecuta los triggers del mismo evento por nombre. Este se
    # ejecuta después de sincronizar_mensualidad_desde_pago, que guarda las fechas.
    op.execute("""
        CREATE TRIGGER sincronizar_mensualidad_desde_pago_y_activar
        AFTER INSERT ON pago
        FOR EACH ROW WHEN (NEW.vehiculo_id IS NOT NULL)
        EXECUTE FUNCTION activar_mensualidad_desde_pago()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER sincronizar_mensualidad_desde_pago_y_activar ON pago")
    op.execute("DROP FUNCTION activar_mensualidad_desde_pago()")
