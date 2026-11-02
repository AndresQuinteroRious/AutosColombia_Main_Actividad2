"""agregar_rol_usuario

Revision ID: b7e2f3c4a91d
Revises: agregar_direccion_a_operador
"""

from alembic import op
import sqlalchemy as sa


revision = "b7e2f3c4a91d"
down_revision = "agregar_direccion_a_operador"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuario",
        sa.Column("rol", sa.Text(), nullable=False, server_default="OPERADOR"),
    )
    op.create_check_constraint(
        "ck_usuario_rol_valido",
        "usuario",
        "rol IN ('ADMINISTRADOR', 'ASISTENTE', 'OPERADOR')",
    )
    op.execute("UPDATE usuario SET rol = 'OPERADOR' WHERE rol IS NULL OR rol = ''")
    op.alter_column("usuario", "rol", server_default=None)


def downgrade() -> None:
    op.drop_constraint("ck_usuario_rol_valido", "usuario", type_="check")
    op.drop_column("usuario", "rol")
