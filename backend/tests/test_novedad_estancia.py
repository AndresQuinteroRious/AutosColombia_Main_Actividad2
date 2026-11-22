from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.models import Novedad
from app.schemas.novedad import NovedadCrear, NovedadVehiculoCrear
from app.services.novedad import NovedadError, create_novedad, create_vehicle_novedad


def test_vehiculo_sin_estancia_no_guarda():
    session = MagicMock()
    session.get.return_value = SimpleNamespace(id=8)
    session.scalar.return_value = None
    with pytest.raises(NovedadError, match='no tiene una estancia abierta'):
        create_vehicle_novedad(session, NovedadVehiculoCrear(vehiculo_id=8, descripcion='Prueba'))
    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_novedad_asociada_a_estancia_abierta():
    session = MagicMock()
    session.get.return_value = SimpleNamespace(id=8, placa='ABC123')
    session.scalar.return_value = SimpleNamespace(
        id=12, entrada=datetime(2026, 11, 15, tzinfo=timezone.utc), salida=None,
        celda=SimpleNamespace(codigo='A1'),
    )

    def refresh(record):
        record.id = 20
        record.fecha = datetime(2026, 11, 15, tzinfo=timezone.utc)

    session.refresh.side_effect = refresh
    result = create_vehicle_novedad(session, NovedadVehiculoCrear(vehiculo_id=8, descripcion='Prueba'))
    record = session.add.call_args.args[0]
    assert record.id_estancia == 12 and record.vehiculo_id == 8
    assert result.id_estancia == 12 and result.celda == 'A1'
    assert result.placa == 'ABC123' and result.descripcion == 'Prueba'


@pytest.mark.parametrize('estancia, status', [(None, 404), (SimpleNamespace(salida=True), 409)])
def test_rechaza_estancia_inexistente_o_cerrada(estancia, status):
    session = MagicMock()
    session.scalar.return_value = estancia
    with pytest.raises(NovedadError) as error:
        create_novedad(session, NovedadCrear(id_estancia=12, descripcion='Prueba'))
    assert error.value.status_code == status
    session.add.assert_not_called()


def test_fk_estancia_restringe_borrado():
    column = Novedad.__table__.c.id_estancia
    fk, = column.foreign_keys
    assert fk.target_fullname == 'estancia.id'
    assert fk.ondelete == 'RESTRICT'
    assert column.nullable  # Preserva las novedades anteriores sin inventar una estancia.


def test_historial_muestra_estancia_y_conserva_novedades_anteriores():
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session
    from app.services.novedad import list_vehicle_history

    engine = create_engine('sqlite://')
    with engine.connect() as connection:
        for sql in (
            'CREATE TABLE vehiculo (id INTEGER, placa TEXT)',
            'CREATE TABLE celda (id INTEGER, codigo TEXT)',
            'CREATE TABLE estancia (id INTEGER, celda_id INTEGER, entrada TIMESTAMP, salida TIMESTAMP)',
            'CREATE TABLE novedad (id INTEGER, vehiculo_id INTEGER, id_estancia INTEGER, descripcion TEXT, fecha TIMESTAMP)',
            "INSERT INTO vehiculo VALUES (1, 'ABC123')",
            "INSERT INTO celda VALUES (1, 'A1')",
            "INSERT INTO estancia VALUES (12, 1, '2026-11-15 08:00:00', NULL)",
            "INSERT INTO novedad VALUES (1, 1, 12, 'Nueva', '2026-11-15 09:00:00'), "
            "(2, NULL, NULL, 'Anterior', '2026-11-14 09:00:00')",
        ):
            connection.execute(text(sql))
        connection.commit()
        with Session(connection) as session:
            result = list_vehicle_history(session, None, None, None, 0, 10)
            assert result['total'] == 2
            linked, old = result['items']
            assert linked.id_estancia == 12 and linked.celda == 'A1'
            assert linked.entrada is not None and linked.descripcion == 'Nueva'
            assert old.id_estancia is None and old.descripcion == 'Anterior'
        with Session(connection) as session:
            result = list_vehicle_history(session, datetime(2026, 11, 15).date(), None, 'ABC', 0, 10)
            assert result['total'] == 1
    engine.dispose()
