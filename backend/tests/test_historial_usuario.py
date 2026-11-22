import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services.estancia import ServicioEstancia


def test_opciones_usuarios_http():
    import asyncio
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.database import get_session
    from app.routers.usuarios import get_current_user
    from types import SimpleNamespace

    class Consulta:
        def order_by(self, *args):
            return self

        def all(self):
            return [SimpleNamespace(id=7, nombre='Usuario real', documento='DOC7')]

    class Sesion:
        def query(self, modelo):
            from app.models import Usuario
            assert modelo is Usuario
            return Consulta()

    async def consultar():
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.get('/usuarios/opciones-historial')
            assert response.status_code == 200
            assert response.json() == [{'id': 7, 'nombre': 'Usuario real', 'documento': 'DOC7'}]

    app.dependency_overrides[get_session] = lambda: Sesion()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(rol='EMPLEADO')
    try:
        asyncio.run(consultar())
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.parametrize('usuario, ids', [
    (' aNA ', [3, 2, 1]),
    ('luis', [1]),
    ('inexistente', []),
    ('%', [3]),
    ('   ', [3, 2, 1]),
])
def test_usuario_en_entrada_o_salida_y_paginacion(usuario, ids):
    # Tablas mínimas en memoria: no se conecta ni modifica PostgreSQL.
    engine = create_engine('sqlite://')
    with engine.connect() as connection:
        for ddl in (
            'CREATE TABLE vehiculo (id INTEGER, placa TEXT)',
            'CREATE TABLE celda (id INTEGER, codigo TEXT)',
            'CREATE TABLE operador (id INTEGER, nombre TEXT, documento TEXT)',
            'CREATE TABLE estancia (id INTEGER, vehiculo_id INTEGER, celda_id INTEGER, '
            'operador_entrada_id INTEGER, operador_salida_id INTEGER, entrada TIMESTAMP, salida TIMESTAMP)',
            "INSERT INTO vehiculo VALUES (1, 'ABC123')",
            "INSERT INTO celda VALUES (1, 'A1')",
            "INSERT INTO operador VALUES (1, 'Ana Pérez', 'DOC1'), (2, 'Luis Gómez', 'DOC2'), (3, 'Nombre % literal', NULL)",
            "INSERT INTO estancia VALUES "
            "(1, 1, 1, 1, 2, '2026-11-01 10:00:00', '2026-11-01 11:00:00'), "
            "(2, 1, 1, 1, NULL, '2026-11-02 10:00:00', NULL), "
            "(3, 1, 1, 3, 1, '2026-11-03 10:00:00', '2026-11-03 11:00:00')",
        ):
            connection.execute(text(ddl))
        connection.execute(text("CREATE TABLE usuario (id INTEGER, documento TEXT)"))
        connection.execute(text("INSERT INTO usuario VALUES (10, 'DOC1'), (20, 'DOC2')"))
        connection.commit()
        for user_id, expected in ((10, [3, 2, 1]), (20, [1]), (99, [])):
            with Session(connection) as session:
                page = ServicioEstancia(session).historial(
                    None, None, None, 0, 10, usuario_id=user_id,
                )
                assert page.total == len(expected)
                assert [item.id for item in page.items] == expected
        with Session(connection) as session:
            page = ServicioEstancia(session).historial(None, None, None, 0, 1, usuario=usuario)
            assert page.total == len(ids)
            assert [item.id for item in page.items] == ids[:1]
        with Session(connection) as session:
            page = ServicioEstancia(session).historial(None, None, None, 1, 10, usuario=usuario)
            assert [item.id for item in page.items] == ids[1:]
        with Session(connection) as session:
            page = ServicioEstancia(session).historial(
                None, None, 'XYZ', 0, 10, usuario=usuario,
            )
            assert page.total == 0
            assert page.items == []
    engine.dispose()
