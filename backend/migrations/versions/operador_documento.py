"""Permitir asociar cada operador con el documento del usuario."""

from alembic import context, op
import sqlalchemy as sa


revision = "operador_documento"
down_revision = "novedad_id_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if context.is_offline_mode():
        op.add_column("operador", sa.Column("documento", sa.Text(), nullable=True))
        op.create_unique_constraint("uq_operador_documento", "operador", ["documento"])
        return

    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("operador")}
    if "documento" not in columns:
        op.add_column("operador", sa.Column("documento", sa.Text(), nullable=True))
    constraints = {constraint["name"] for constraint in sa.inspect(op.get_bind()).get_unique_constraints("operador")}
    if "uq_operador_documento" not in constraints:
        op.create_unique_constraint("uq_operador_documento", "operador", ["documento"])


def downgrade() -> None:
    op.drop_constraint("uq_operador_documento", "operador", type_="unique")
    op.drop_column("operador", "documento")
