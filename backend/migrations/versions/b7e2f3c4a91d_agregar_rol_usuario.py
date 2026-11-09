"""agregar_rol_usuario

Revision ID: b7e2f3c4a91d
Revises: agregar_direccion_a_operador
"""

from alembic import context, op
import sqlalchemy as sa


revision = "b7e2f3c4a91d"
down_revision = "agregar_direccion_a_operador"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if context.is_offline_mode():
        op.add_column(
            "usuario",
            sa.Column("rol", sa.Text(), nullable=False, server_default="OPERADOR"),
        )
        op.create_check_constraint(
            "ck_usuario_rol_valido", "usuario",
            "rol IN ('ADMINISTRADOR', 'ASISTENTE', 'OPERADOR')",
        )
        op.execute("UPDATE usuario SET rol = 'OPERADOR' WHERE rol IS NULL OR rol = ''")
        op.alter_column("usuario", "rol", server_default=None)
        return
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("usuario")}
    rol_preexistente = "rol" in columns
    if "rol" not in columns:
        op.add_column(
            "usuario",
            sa.Column("rol", sa.Text(), nullable=False, server_default="OPERADOR"),
        )
        op.execute("UPDATE usuario SET rol = 'OPERADOR' WHERE rol IS NULL OR rol = ''")
        op.alter_column("usuario", "rol", server_default=None)

    constraints = {constraint["name"] for constraint in sa.inspect(op.get_bind()).get_check_constraints("usuario")}
    # Si rol ya existe, puede contener valores de la revisión siguiente
    # (por ejemplo, EMPLEADO); c6a9f0d23b0a aplicará la restricción final.
    if "ck_usuario_rol_valido" not in constraints and not rol_preexistente:
        op.create_check_constraint(
            "ck_usuario_rol_valido",
            "usuario",
            "rol IN ('ADMINISTRADOR', 'ASISTENTE', 'OPERADOR')",
        )


def downgrade() -> None:
    op.drop_constraint("ck_usuario_rol_valido", "usuario", type_="check")
    op.drop_column("usuario", "rol")
