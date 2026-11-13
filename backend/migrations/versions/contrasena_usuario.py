"""Agregar contraseña protegida y cambio obligatorio al usuario nuevo."""

from alembic import op
import sqlalchemy as sa


revision = "contrasena_usuario"
down_revision = "operador_documento"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuario", sa.Column("contrasena_hash", sa.Text(), nullable=True))
    op.add_column(
        "usuario",
        sa.Column("requiere_cambio_contrasena", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("usuario", "requiere_cambio_contrasena", server_default=None)


def downgrade() -> None:
    op.drop_column("usuario", "requiere_cambio_contrasena")
    op.drop_column("usuario", "contrasena_hash")
