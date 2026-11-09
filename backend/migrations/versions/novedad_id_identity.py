"""Generar automáticamente el identificador de cada novedad."""

from alembic import op


revision = "novedad_id_identity"
down_revision = "novedad_vehiculo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE novedad ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY")
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('novedad', 'id'),
            COALESCE(MAX(id), 1),
            MAX(id) IS NOT NULL
        )
        FROM novedad
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE novedad ALTER COLUMN id DROP IDENTITY")
