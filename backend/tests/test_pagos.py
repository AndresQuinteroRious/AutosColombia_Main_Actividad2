from collections.abc import Iterator
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import get_session
from app.main import app
from app.models import Pago, Vehiculo


@pytest.fixture
def pagos_client() -> Iterator[tuple[TestClient, MagicMock]]:
    session = MagicMock()
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    try:
        yield client, session
    finally:
        client.close()
        app.dependency_overrides.pop(get_session)


def test_list_plates_orders_by_plate(pagos_client: tuple[TestClient, MagicMock]) -> None:
    client, session = pagos_client
    session.execute.return_value = [
        SimpleNamespace(id=8, placa="ABC123"),
        SimpleNamespace(id=1, placa="XYZ987"),
    ]

    response = client.get("/pagos/placas")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 8, "placa": "ABC123"},
        {"id": 1, "placa": "XYZ987"},
    ]
    assert "ORDER BY vehiculo.placa" in str(session.execute.call_args.args[0])


@pytest.mark.parametrize("valor", [125000, 250000])
def test_create_payment_links_registered_vehicle(
    pagos_client: tuple[TestClient, MagicMock], valor: int,
) -> None:
    client, session = pagos_client
    vehicle = Vehiculo(id=8, placa="ABC123")
    session.get.return_value = vehicle

    def refresh(pago: Pago) -> None:
        pago.id = 1
        pago.fecha = datetime(2026, 1, 1, tzinfo=timezone.utc)
        pago.vehiculo = vehicle

    # Simula los datos que la base devuelve al refrescar la instancia.
    session.refresh.side_effect = refresh
    response = client.post("/pagos", json={"valor": valor, "periodo": "Enero", "vehiculo_id": 8})

    assert response.status_code == 201
    assert response.json()["vehiculo_id"] == 8
    assert response.json()["placa"] == "ABC123"
    assert response.json()["valor"] == str(valor)
    session.commit.assert_called_once()


@pytest.mark.parametrize(
    ("valor", "detail"),
    [
        (1000, "Selecciona una tarifa válida para moto o automóvil."),
        (125000, "Selecciona la placa de un vehículo registrado."),
    ],
)
def test_create_payment_rejects_invalid_tariff_or_unknown_vehicle(
    pagos_client: tuple[TestClient, MagicMock], valor: int, detail: str,
) -> None:
    client, session = pagos_client
    session.get.return_value = None

    response = client.post("/pagos", json={"valor": valor, "periodo": "Enero", "vehiculo_id": 8})

    assert response.status_code == 422
    assert response.json() == {"detail": detail}
    session.commit.assert_not_called()
