from datetime import datetime
from decimal import Decimal
from functools import wraps
from zoneinfo import ZoneInfo

from sqlalchemy import func, select, text, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Pago, TarifaPago, Vehiculo
from app.schemas.pago import PagoActualizar, PagoCrear, PlacaPago, TarifasPago

BOGOTA = ZoneInfo("America/Bogota")
PAGO_DUPLICADO = "La placa ya tiene un pago registrado."


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
            constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
            if code == "23505" and constraint == "uq_pago_vehiculo":
                raise PagoError(409, PAGO_DUPLICADO) from None
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


def find_tariffs(session: Session, *, for_payment: bool = False) -> TarifaPago:
    # El pago conserva la tarifa vigente hasta que termina su transacción.
    tariffs = session.get(TarifaPago, 1, with_for_update={"read": True} if for_payment else None)
    if tariffs is None:
        raise PagoError(503, "Las tarifas de pagos no están configuradas.")
    return tariffs


@database_operation
def get_tariffs(session: Session) -> TarifasPago:
    return TarifasPago.model_validate(find_tariffs(session))


@database_operation
def update_tariffs(session: Session, data: TarifasPago) -> TarifasPago:
    tariffs = session.scalar(
        update(TarifaPago).where(TarifaPago.id == 1).values(**data.model_dump()).returning(TarifaPago)
    )
    if tariffs is None:
        raise PagoError(503, "Las tarifas de pagos no están configuradas.")
    result = TarifasPago.model_validate(tariffs)
    session.commit()
    return result


@database_operation
def create_pago(session: Session, data: PagoCrear) -> Pago:
    if session.scalar(select(Pago.id).where(Pago.vehiculo_id == data.vehiculo_id).limit(1)) is not None:
        raise PagoError(409, PAGO_DUPLICADO)
    validate_tariff(session, data.vehiculo_id, data.valor)
    fecha = datetime.now(BOGOTA)
    pago = Pago(
        valor=data.valor,
        vehiculo_id=data.vehiculo_id,
        fecha=fecha,
        periodo=data.periodo if data.periodo is not None else fecha.date().isoformat(),
    )
    session.add(pago)
    session.commit()
    session.refresh(pago)
    return pago


def validate_tariff(session: Session, vehiculo_id: int, valor: Decimal) -> None:
    vehicle = session.get(Vehiculo, vehiculo_id)
    if vehicle is None:
        raise PagoError(422, "Selecciona la placa de un vehículo registrado.")
    tariffs = find_tariffs(session, for_payment=True)
    tarifa = {"AUTOMOVIL": tariffs.automovil, "MOTOCICLETA": tariffs.motocicleta}.get(vehicle.tipo)
    if tarifa is None:
        raise PagoError(422, "Este tipo de vehículo no tiene una tarifa configurada.")
    if valor != tarifa:
        raise PagoError(422, "El valor no corresponde a la tarifa del vehículo.")


@database_operation
def list_plates(session: Session) -> list[PlacaPago]:
    tariffs = find_tariffs(session)
    amounts = {"AUTOMOVIL": tariffs.automovil, "MOTOCICLETA": tariffs.motocicleta}
    rows = session.execute(text("""
        SELECT v.id, v.placa, v.tipo,
               EXISTS (SELECT 1 FROM pago WHERE vehiculo_id = v.id) AS tiene_pago,
               COALESCE(m.estado = 'activo', false) AS mensualidad_activa
        FROM vehiculo v
        LEFT JOIN LATERAL (
            SELECT estado FROM mensualidad
            WHERE id_vehiculo = v.id
            ORDER BY id_mensualidad DESC
            LIMIT 1
        ) m ON true
        ORDER BY v.placa
    """))
    return [
        PlacaPago(
            id=row.id, placa=row.placa, tipo=row.tipo, tarifa=amounts.get(row.tipo),
            tiene_pago=row.tiene_pago, pago_activo=row.tiene_pago and row.mensualidad_activa,
        )
        for row in rows
    ]


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
    vehiculo_id = data.vehiculo_id or pago.vehiculo_id
    if vehiculo_id is not None and (
        vehiculo_id != pago.vehiculo_id or (data.valor is not None and data.valor != pago.valor)
    ):
        validate_tariff(session, vehiculo_id, data.valor if data.valor is not None else pago.valor)
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
