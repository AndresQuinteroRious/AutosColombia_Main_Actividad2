"""Asociar novedades con vehículos.

Revision ID: novedad_vehiculo
Revises: 4be64630245c, c6a9f0d23b0a
"""
from alembic import op
import sqlalchemy as sa


revision = "novedad_vehiculo"
down_revision = ("4be64630245c", "c6a9f0d23b0a")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("novedad", sa.Column("vehiculo_id", sa.BigInteger(), nullable=True))
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
