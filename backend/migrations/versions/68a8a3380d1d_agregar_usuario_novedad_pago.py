"""agregar_usuario_novedad_pago

Revision ID: 68a8a3380d1d
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa


revision = '68a8a3380d1d'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column("documento", sa.Text(), nullable=False),
        sa.Column("telefono", sa.Text(), nullable=False),
        sa.Column("fecha_vencimiento", sa.Date(), nullable=False),
        sa.UniqueConstraint("documento", name="uq_usuario_documento"),
        sa.CheckConstraint("nombre ~ '[^[:space:]]'", name="ck_usuario_nombre_no_vacio"),
        sa.CheckConstraint("documento ~ '[^[:space:]]'", name="ck_usuario_documento_no_vacio"),
        sa.CheckConstraint("telefono ~ '[^[:space:]]'", name="ck_usuario_telefono_no_vacio"),
    )
    op.create_table(
        "novedad",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("descripcion ~ '[^[:space:]]'", name="ck_novedad_descripcion_no_vacio"),
    )
    op.create_table(
        "pago",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("periodo", sa.Text(), nullable=False),
        sa.CheckConstraint("valor > 0", name="ck_pago_valor_positivo"),
        sa.CheckConstraint("periodo ~ '[^[:space:]]'", name="ck_pago_periodo_no_vacio"),
    )


def downgrade() -> None:
    op.drop_table("pago")
    op.drop_table("novedad")
    op.drop_table("usuario")
