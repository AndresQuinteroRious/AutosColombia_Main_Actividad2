"""agregar_turno_horas_usuario

Revision ID: c6a9f0d23b0a
Revises: b7e2f3c4a91d
"""

from alembic import context, op
import sqlalchemy as sa


revision = "c6a9f0d23b0a"
down_revision = "b7e2f3c4a91d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if context.is_offline_mode():
        op.add_column("usuario", sa.Column("turno", sa.Text(), nullable=False, server_default="MAÑANA"))
        op.add_column("usuario", sa.Column("horas_semana", sa.Integer(), nullable=False, server_default="42"))
        op.add_column("usuario", sa.Column("ausentismo_horas", sa.Integer(), nullable=False, server_default="0"))
        op.drop_constraint("ck_usuario_rol_valido", "usuario", type_="check")
        op.execute("UPDATE usuario SET rol = 'EMPLEADO' WHERE rol IN ('ASISTENTE', 'OPERADOR') OR rol IS NULL OR rol = ''")
        for name, condition in (
            ("ck_usuario_rol_valido", "rol IN ('ADMINISTRADOR', 'EMPLEADO')"),
            ("ck_usuario_turno_valido", "turno IN ('MAÑANA', 'TARDE', 'NOCHE', 'RESPALDO')"),
            ("ck_usuario_horas_semana_valida", "horas_semana BETWEEN 1 AND 84"),
            ("ck_usuario_ausentismo_horas_valida", "ausentismo_horas BETWEEN 0 AND 84"),
        ):
            op.create_check_constraint(name, "usuario", condition)
        for column in ("turno", "horas_semana", "ausentismo_horas"):
            op.alter_column("usuario", column, server_default=None)
        return
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("usuario")}
    if "turno" not in columns:
        op.add_column("usuario", sa.Column("turno", sa.Text(), nullable=False, server_default="MAÑANA"))
        op.alter_column("usuario", "turno", server_default=None)
    if "horas_semana" not in columns:
        op.add_column("usuario", sa.Column("horas_semana", sa.Integer(), nullable=False, server_default="42"))
        op.alter_column("usuario", "horas_semana", server_default=None)
    if "ausentismo_horas" not in columns:
        op.add_column("usuario", sa.Column("ausentismo_horas", sa.Integer(), nullable=False, server_default="0"))
        op.alter_column("usuario", "ausentismo_horas", server_default=None)

    constraints = {constraint["name"] for constraint in sa.inspect(op.get_bind()).get_check_constraints("usuario")}
    if "ck_usuario_rol_valido" in constraints:
        op.drop_constraint("ck_usuario_rol_valido", "usuario", type_="check")
    op.execute("UPDATE usuario SET rol = 'EMPLEADO' WHERE rol IN ('ASISTENTE', 'OPERADOR') OR rol IS NULL OR rol = ''")
    constraints = {constraint["name"] for constraint in sa.inspect(op.get_bind()).get_check_constraints("usuario")}
    checks = (
        ("ck_usuario_rol_valido", "rol IN ('ADMINISTRADOR', 'EMPLEADO')"),
        ("ck_usuario_turno_valido", "turno IN ('MAÑANA', 'TARDE', 'NOCHE', 'RESPALDO')"),
        ("ck_usuario_horas_semana_valida", "horas_semana BETWEEN 1 AND 84"),
        ("ck_usuario_ausentismo_horas_valida", "ausentismo_horas BETWEEN 0 AND 84"),
    )
    for name, condition in checks:
        if name not in constraints:
            op.create_check_constraint(name, "usuario", condition)


def downgrade() -> None:
    op.drop_constraint("ck_usuario_ausentismo_horas_valida", "usuario", type_="check")
    op.drop_constraint("ck_usuario_horas_semana_valida", "usuario", type_="check")
    op.drop_constraint("ck_usuario_turno_valido", "usuario", type_="check")
    op.drop_constraint("ck_usuario_rol_valido", "usuario", type_="check")
    op.create_check_constraint(
        "ck_usuario_rol_valido",
        "usuario",
        "rol IN ('ADMINISTRADOR', 'ASISTENTE', 'OPERADOR')",
    )
    op.drop_column("usuario", "ausentismo_horas")
    op.drop_column("usuario", "horas_semana")
    op.drop_column("usuario", "turno")
