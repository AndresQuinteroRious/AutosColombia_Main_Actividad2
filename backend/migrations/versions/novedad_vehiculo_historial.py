"""Asociar novedades con vehículos.

Revision ID: novedad_vehiculo
Revises: 4be64630245c, c6a9f0d23b0a
"""
from alembic import context, op
import sqlalchemy as sa


revision = "novedad_vehiculo"
down_revision = ("4be64630245c", "c6a9f0d23b0a")
branch_labels = None
depends_on = None


def upgrade() -> None:
    if context.is_offline_mode():
        op.add_column("novedad", sa.Column("vehiculo_id", sa.BigInteger(), nullable=True))
        op.create_foreign_key(
            "fk_novedad_vehiculo", "novedad", "vehiculo",
            ["vehiculo_id"], ["id"], ondelete="SET NULL",
        )
        return
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"]: column for column in inspector.get_columns("novedad")}
    foreign_keys = inspector.get_foreign_keys("novedad")
    if "vehiculo_id" not in columns and "id_vehiculo" in columns:
        # La base existente usaba id_vehiculo; se conserva la relación y sus datos.
        for foreign_key in foreign_keys:
            if foreign_key.get("constrained_columns") == ["id_vehiculo"]:
                op.drop_constraint(foreign_key["name"], "novedad", type_="foreignkey")
        op.alter_column("novedad", "id_vehiculo", new_column_name="vehiculo_id")
        op.alter_column("novedad", "vehiculo_id", type_=sa.BigInteger(), postgresql_using="vehiculo_id::bigint")
        columns["vehiculo_id"] = columns.pop("id_vehiculo")
        foreign_keys = inspector.get_foreign_keys("novedad")
    if "vehiculo_id" not in columns:
        op.add_column("novedad", sa.Column("vehiculo_id", sa.BigInteger(), nullable=True))
    if not any(foreign_key.get("constrained_columns") == ["vehiculo_id"] for foreign_key in foreign_keys):
        op.create_foreign_key(
            "fk_novedad_vehiculo",
            "novedad",
            "vehiculo",
            ["vehiculo_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    op.drop_constraint("fk_novedad_vehiculo", "novedad", type_="foreignkey")
    op.drop_column("novedad", "vehiculo_id")
