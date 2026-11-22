"""Verificaciones de lectura de Inicio sobre PostgreSQL, sin crear ni modificar datos."""
import os

import pytest
from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session

from app.database import get_engine
from app.models import Estancia, Usuario
from app.services.estancia import ServicioEstancia
from app.services.usuario import opciones_historial

pytestmark = pytest.mark.skipif(
    os.getenv('RUN_POSTGRES_TESTS') != '1', reason='Requiere PostgreSQL local.',
)


def test_columnas_y_restricciones_usuario():
    engine = get_engine()
    inspector = inspect(engine)
    columns = {column['name']: column for column in inspector.get_columns('usuario')}
    for nombre in ('turno', 'horas_semana', 'ausentismo_horas'):
        assert not columns[nombre]['nullable']
    constraints = {constraint['name'] for constraint in inspector.get_check_constraints('usuario')}
    assert {
        'ck_usuario_turno_valido', 'ck_usuario_horas_semana_valida',
        'ck_usuario_ausentismo_horas_valida',
    } <= constraints
    with engine.connect() as connection:
        assert connection.scalar(text('SELECT version_num FROM alembic_version')) == 'reparar_columnas_usuario'


def test_usuarios_y_estancias_con_transaccion_previa():
    with Session(get_engine()) as session:
        # Carga completa del modelo, como hace la autenticación antes de la consulta.
        session.scalars(select(Usuario).limit(1)).first()
        assert session.in_transaction()
        usuarios = opciones_historial(session)
        assert len(usuarios) == session.scalar(select(func.count()).select_from(Usuario))
        abiertas = ServicioEstancia(session).abiertas()
        total = session.scalar(select(func.count()).select_from(Estancia).where(Estancia.salida.is_(None)))
        assert len(abiertas) == total
        assert len({estancia.id for estancia in abiertas}) == total
        session.rollback()
