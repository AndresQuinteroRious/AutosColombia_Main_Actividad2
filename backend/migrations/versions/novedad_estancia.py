"""Vincular novedades a estancias sin inventar relaciones para datos anteriores."""
from alembic import op
import sqlalchemy as sa

revision = "novedad_estancia"
down_revision = "contrasena_usuario"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("novedad", sa.Column("id_estancia", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fk_novedad_estancia", "novedad", "estancia", ["id_estancia"], ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_novedad_id_estancia", "novedad", ["id_estancia"])


def downgrade() -> None:
    op.drop_index("ix_novedad_id_estancia", table_name="novedad")
    op.drop_constraint("fk_novedad_estancia", "novedad", type_="foreignkey")
    op.drop_column("novedad", "id_estancia")
