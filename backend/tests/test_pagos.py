from collections.abc import Iterator
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.main import app
from app.models import Pago, TarifaPago, Vehiculo
from app.services import usuario


@pytest.fixture
def pagos_client() -> Iterator[tuple[TestClient, MagicMock]]:
    session = MagicMock()
    session.scalar.return_value = None
    tariff = TarifaPago(id=1, automovil=Decimal("250000"), motocicleta=Decimal("125000"))
    session.get.side_effect = lambda model, *args, **kwargs: tariff if model is TarifaPago else None
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
        SimpleNamespace(id=8, placa="ABC123", tipo="MOTOCICLETA", tiene_pago=True, mensualidad_activa=True),
        SimpleNamespace(id=1, placa="XYZ987", tipo="AUTOMOVIL", tiene_pago=False, mensualidad_activa=False),
    ]

    response = client.get("/pagos/placas")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 8, "placa": "ABC123", "tipo": "MOTOCICLETA", "tarifa": 125000,
         "tiene_pago": True, "pago_activo": True},
        {"id": 1, "placa": "XYZ987", "tipo": "AUTOMOVIL", "tarifa": 250000,
         "tiene_pago": False, "pago_activo": False},
    ]
    assert "ORDER BY v.placa" in str(session.execute.call_args.args[0])


@pytest.mark.parametrize("concurrent", [False, True])
def test_create_rejects_duplicate_plate(
    pagos_client: tuple[TestClient, MagicMock], concurrent: bool,
) -> None:
    client, session = pagos_client
    if concurrent:
        get_tariff = session.get.side_effect
        session.get.side_effect = lambda model, *args, **kwargs: (
            get_tariff(model) if model is TarifaPago else Vehiculo(tipo="AUTOMOVIL")
        )
        driver_error = Exception("Detalle interno")
        driver_error.sqlstate = "23505"
        driver_error.diag = SimpleNamespace(constraint_name="uq_pago_vehiculo")
        session.commit.side_effect = IntegrityError("INSERT", {}, driver_error)
    else:
        session.scalar.return_value = 5

    response = client.post("/pagos", json={"valor": 250000, "vehiculo_id": 8})

    assert response.status_code == 409
    assert response.json() == {"detail": "La placa ya tiene un pago registrado."}
    if concurrent:
        session.rollback.assert_called_once()
    else:
        session.add.assert_not_called()


@pytest.mark.parametrize(("tipo", "valor"), [("MOTOCICLETA", 135000), ("AUTOMOVIL", 260000)])
def test_create_payment_links_registered_vehicle(
    pagos_client: tuple[TestClient, MagicMock], tipo: str, valor: int,
) -> None:
    client, session = pagos_client
    vehicle = Vehiculo(id=8, placa="ABC123", tipo=tipo)
    tariff = TarifaPago(id=1, automovil=Decimal("260000"), motocicleta=Decimal("135000"))
    session.get.side_effect = lambda model, *args, **kwargs: tariff if model is TarifaPago else vehicle

    def refresh(pago: Pago) -> None:
        pago.id = 1
        pago.vehiculo = vehicle

    # Simula los datos que la base devuelve al refrescar la instancia.
    session.refresh.side_effect = refresh
    response = client.post("/pagos", json={"valor": valor, "vehiculo_id": 8})

    assert response.status_code == 201
    assert response.json()["vehiculo_id"] == 8
    assert response.json()["placa"] == "ABC123"
    assert response.json()["valor"] == str(valor)
    pago = session.add.call_args.args[0]
    assert response.json()["fecha"] == pago.fecha.isoformat()
    assert pago.periodo == pago.fecha.date().isoformat()
    session.commit.assert_called_once()


@pytest.mark.parametrize(
    ("tipo", "valor", "detail"),
    [
        ("MOTOCICLETA", 250000, "El valor no corresponde a la tarifa del vehículo."),
        ("AUTOMOVIL", 125000, "El valor no corresponde a la tarifa del vehículo."),
        (None, 125000, "Selecciona la placa de un vehículo registrado."),
    ],
)
def test_create_payment_rejects_invalid_tariff_or_unknown_vehicle(
    pagos_client: tuple[TestClient, MagicMock], tipo: str | None, valor: int, detail: str,
) -> None:
    client, session = pagos_client
    vehicle = Vehiculo(tipo=tipo) if tipo is not None else None
    get_tariff = session.get.side_effect
    session.get.side_effect = lambda model, *args, **kwargs: (
        get_tariff(model) if model is TarifaPago else vehicle
    )

    response = client.post("/pagos", json={"valor": valor, "periodo": "Enero", "vehiculo_id": 8})

    assert response.status_code == 422
    assert response.json() == {"detail": detail}
    session.commit.assert_not_called()


def test_get_current_tariffs(pagos_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = pagos_client
    response = client.get("/pagos/tarifas")

    assert response.status_code == 200
    assert response.json() == {"automovil": 250000, "motocicleta": 125000}


@pytest.mark.parametrize(
    ("role", "new_amount", "status"),
    [(None, 300000, 401), ("EMPLEADO", 300000, 403),
     ("ADMINISTRADOR", 0, 422), ("ADMINISTRADOR", 300000.25, 200)],
)
def test_update_tariffs_checks_role_and_amount(
    pagos_client: tuple[TestClient, MagicMock], monkeypatch: pytest.MonkeyPatch,
    role: str | None, new_amount: float, status: int,
) -> None:
    client, session = pagos_client
    monkeypatch.setattr(
        usuario, "obtener_usuario_por_token", lambda database, token: SimpleNamespace(rol=role),
    )
    session.scalar.return_value = TarifaPago(
        id=1, automovil=Decimal(str(new_amount)), motocicleta=Decimal("125000"),
    )
    payload = {"automovil": new_amount, "motocicleta": 125000}
    headers = {"Authorization": "Bearer test-session"} if role else {}

    response = client.put("/pagos/tarifas", headers=headers, json=payload)

    assert response.status_code == status
    if status == 200:
        assert response.json() == payload
        query = session.scalar.call_args.args[0]
        assert str(query).startswith("UPDATE tarifa_pago SET")
        assert query.compile().params["automovil"] == Decimal(str(new_amount))
        session.commit.assert_called_once()
    else:
        session.scalar.assert_not_called()
        session.commit.assert_not_called()
