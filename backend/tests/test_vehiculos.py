from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.schemas.celda import CeldaActualizar
from app.schemas.vehiculo import VehiculoActualizar, VehiculoCrear
from app.services.vehiculo import VehiculoError, create_vehicle, delete_vehicle, update_vehicle


@pytest.mark.parametrize("field", ["placa", "color", "modelo", "marca", "tipo"])
def test_patch_rejects_explicit_null(field):
    with pytest.raises(ValidationError):
        VehiculoActualizar(**{field: None})


@pytest.mark.parametrize("field", ["placa", "color", "marca", "tipo"])
def test_patch_rejects_blank_text(field):
    with pytest.raises(ValidationError):
        VehiculoActualizar(**{field: " \t\n"})


def test_patch_only_supplied_fields_and_no_id():
    assert VehiculoActualizar(placa=" abc123 ").model_dump(exclude_unset=True) == {"placa": "ABC123"}
    assert VehiculoActualizar().model_dump(exclude_unset=True) == {}
    with pytest.raises(ValidationError):
        VehiculoActualizar(id=1)


def test_creation_requires_every_field():
    with pytest.raises(ValidationError):
        VehiculoCrear(placa="ABC123")


@pytest.mark.parametrize("schema", [VehiculoActualizar, CeldaActualizar])
def test_parking_type_contract(
    schema: type[VehiculoActualizar] | type[CeldaActualizar],
) -> None:
    assert schema(tipo="AUTOMOVIL").tipo == "AUTOMOVIL"
    assert schema(tipo=" MOTOCICLETA ").tipo == "MOTOCICLETA"
    for tipo in ("MOTO", "CAMION", "FURGON", "CAMIONETA"):
        with pytest.raises(ValidationError):
            schema(tipo=tipo)


def test_vehicle_write_reports_the_status_returned_by_database() -> None:
    session = MagicMock()
    results = session.execute.return_value.mappings.return_value
    results.first.return_value = {"id_mensualidad": 1}
    results.one.return_value = {"estado": "desactivado"}
    data = VehiculoCrear(
        placa="ABC123", color="Azul", modelo=2024, marca="Marca",
        tipo="AUTOMOVIL", estado_mensualidad="activo",
    )

    created = create_vehicle(session, data)
    updated = update_vehicle(session, 1, VehiculoActualizar(estado_mensualidad="activo"))

    assert created.estado_mensualidad == "desactivado"
    assert updated.estado_mensualidad == "desactivado"


def test_delete_foreign_key_conflict_rolls_back_without_related_deletes():
    session = MagicMock()
    vehicle = session.get.return_value
    driver_error = Exception("private database details")
    driver_error.sqlstate = "23503"
    driver_error.diag = SimpleNamespace(constraint_name="some_foreign_key")
    session.commit.side_effect = IntegrityError("DELETE", {}, driver_error)
    with pytest.raises(VehiculoError) as result:
        delete_vehicle(session, 1)
    assert result.value.status_code == 409
    assert "private" not in result.value.detail
    session.rollback.assert_called_once()
    session.delete.assert_called_once_with(vehicle)
