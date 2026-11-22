from decimal import Decimal
from functools import wraps

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Pago, Vehiculo
from app.schemas.pago import PagoActualizar, PagoCrear, PlacaPago


class PagoError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def database_operation(operation):
    """Centraliza rollback y mensajes públicos sin detalles del driver."""
    @wraps(operation)
    def wrapped(session: Session, *args, **kwargs):
        try:
            return operation(session, *args, **kwargs)
        except IntegrityError as error:
            session.rollback()
            code = getattr(error.orig, "sqlstate", None)
            if code == "23503":
                raise PagoError(409, "La operación entra en conflicto con un registro relacionado.") from None
            if code in {"23502", "23514"}:
                raise PagoError(422, "Los datos incumplen las restricciones del pago.") from None
            raise PagoError(409, "La operación entra en conflicto con los datos existentes.") from None
        except SQLAlchemyError:
            session.rollback()
            raise PagoError(503, "No se pudo completar la operación con la base de datos.") from None
    return wrapped


def find_pago(session: Session, pago_id: int) -> Pago:
    pago = session.get(Pago, pago_id)
    if pago is None:
        raise PagoError(404, "Pago no encontrado.")
    return pago


@database_operation
def create_pago(session: Session, data: PagoCrear) -> Pago:
    validate_tariff(data.valor)
    validate_vehicle(session, data.vehiculo_id)
    pago = Pago(**data.model_dump())
    session.add(pago)
    session.commit()
    session.refresh(pago)
    return pago


def validate_tariff(valor: Decimal) -> None:
    if valor not in {125000, 250000}:
        raise PagoError(422, "Selecciona una tarifa válida para moto o automóvil.")


def validate_vehicle(session: Session, vehiculo_id: int) -> None:
    if session.get(Vehiculo, vehiculo_id) is None:
        raise PagoError(422, "Selecciona la placa de un vehículo registrado.")


@database_operation
def list_plates(session: Session) -> list[PlacaPago]:
    rows = session.execute(select(Vehiculo.id, Vehiculo.placa).order_by(Vehiculo.placa))
    return [PlacaPago(id=row.id, placa=row.placa) for row in rows]


@database_operation
def list_pagos(session: Session, offset: int, limit: int) -> dict:
    total = session.scalar(select(func.count()).select_from(Pago))
    items = list(session.scalars(select(Pago).order_by(Pago.id).offset(offset).limit(limit)))
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@database_operation
def get_pago(session: Session, pago_id: int) -> Pago:
    return find_pago(session, pago_id)


@database_operation
def update_pago(session: Session, pago_id: int, data: PagoActualizar) -> Pago:
    pago = find_pago(session, pago_id)
    if data.vehiculo_id is not None or pago.vehiculo_id is not None:
        validate_tariff(data.valor if data.valor is not None else pago.valor)
    if data.vehiculo_id is not None:
        validate_vehicle(session, data.vehiculo_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(pago, key, value)
    session.commit()
    session.refresh(pago)
    return pago


@database_operation
def delete_pago(session: Session, pago_id: int) -> None:
    pago = find_pago(session, pago_id)
    session.delete(pago)
    session.commit()
