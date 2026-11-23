"""Calcular las fechas de mensualidad a partir del último pago del vehículo."""
import sqlalchemy as sa
from alembic import op

revision = "mensualidad_fechas"
down_revision = "pago_vehiculo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # La tabla proviene del respaldo ac.sql y no existía en la cadena de Alembic.
    op.execute("""
        CREATE TABLE IF NOT EXISTS mensualidad (
            id_mensualidad integer PRIMARY KEY,
            estado varchar(15) NOT NULL CHECK (estado IN ('activo', 'desactivado')),
            id_vehiculo bigint NOT NULL REFERENCES vehiculo (id)
        )
    """)
    op.add_column("mensualidad", sa.Column("fecha_inicio", sa.Date(), nullable=True))
    op.add_column(
        "mensualidad",
        sa.Column("fecha_final", sa.Date(), sa.Computed("fecha_inicio + 30", persisted=True)),
    )
    op.execute("""
        CREATE FUNCTION actualizar_fechas_mensualidad(vehiculo bigint) RETURNS void
        LANGUAGE plpgsql AS $$
        DECLARE
            inicio date;
        BEGIN
            IF vehiculo IS NULL THEN
                RETURN;
            END IF;

            -- Comparte el bloqueo usado al asignar id_mensualidad en el servicio de vehículos.
            LOCK TABLE mensualidad IN EXCLUSIVE MODE;
            SELECT (p.fecha AT TIME ZONE 'America/Bogota')::date INTO inicio
            FROM pago p
            WHERE p.vehiculo_id = vehiculo
            ORDER BY p.fecha DESC, p.id DESC
            LIMIT 1;

            UPDATE mensualidad
            SET fecha_inicio = inicio
            WHERE id_mensualidad = (
                SELECT m.id_mensualidad FROM mensualidad m
                WHERE m.id_vehiculo = vehiculo
                ORDER BY m.id_mensualidad DESC
                LIMIT 1
            );

            IF NOT FOUND AND inicio IS NOT NULL THEN
                INSERT INTO mensualidad (id_mensualidad, estado, id_vehiculo, fecha_inicio)
                SELECT COALESCE(MAX(id_mensualidad), 0) + 1, 'desactivado', vehiculo, inicio
                FROM mensualidad;
            END IF;
        END;
        $$
    """)
    op.execute("""
        CREATE FUNCTION sincronizar_mensualidad_desde_pago() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                PERFORM actualizar_fechas_mensualidad(OLD.vehiculo_id);
            ELSIF TG_OP = 'INSERT' THEN
                PERFORM actualizar_fechas_mensualidad(NEW.vehiculo_id);
            ELSE
                PERFORM actualizar_fechas_mensualidad(NEW.vehiculo_id);
                IF OLD.vehiculo_id IS DISTINCT FROM NEW.vehiculo_id THEN
                    PERFORM actualizar_fechas_mensualidad(OLD.vehiculo_id);
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER sincronizar_mensualidad_desde_pago
        AFTER INSERT OR UPDATE OF fecha, vehiculo_id OR DELETE ON pago
        FOR EACH ROW EXECUTE FUNCTION sincronizar_mensualidad_desde_pago()
    """)
    op.execute("""
        SELECT actualizar_fechas_mensualidad(p.vehiculo_id)
        FROM (SELECT DISTINCT vehiculo_id FROM pago WHERE vehiculo_id IS NOT NULL) p
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER sincronizar_mensualidad_desde_pago ON pago")
    op.execute("DROP FUNCTION sincronizar_mensualidad_desde_pago()")
    op.execute("DROP FUNCTION actualizar_fechas_mensualidad(bigint)")
    op.drop_column("mensualidad", "fecha_final")
    op.drop_column("mensualidad", "fecha_inicio")
