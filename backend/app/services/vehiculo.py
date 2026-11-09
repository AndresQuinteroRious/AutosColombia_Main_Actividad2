from functools import wraps

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Vehiculo
from app.schemas.vehiculo import EstadoMensualidad, VehiculoActualizar, VehiculoCrear


class VehiculoError(Exception):
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
            if code == "23505" and constraint == "uq_vehiculo_placa":
                raise VehiculoError(409, "Ya existe un vehículo con esa placa.") from None
            if code == "23503" and constraint == "fk_vehiculo_celda":
                raise VehiculoError(404, "La celda especificada no existe.") from None
            if code == "23503":
                raise VehiculoError(409, "El vehículo tiene registros relacionados y no se puede eliminar.") from None
            if code in {"23502", "23514"}:
                raise VehiculoError(422, "Los datos incumplen las restricciones del vehículo.") from None
            raise VehiculoError(409, "La operación entra en conflicto con los datos existentes.") from None
        except SQLAlchemyError:
            session.rollback()
            raise VehiculoError(503, "No se pudo completar la operación con la base de datos.") from None
    return wrapped


def find_vehicle(session: Session, vehicle_id: int) -> Vehiculo:
    vehicle = session.get(Vehiculo, vehicle_id)
    if vehicle is None:
        raise VehiculoError(404, "Vehículo no encontrado.")
    return vehicle


@database_operation
def create_vehicle(session: Session, data: VehiculoCrear) -> Vehiculo:
    payload = data.model_dump()
    estado_mensualidad = payload.pop("estado_mensualidad")
    vehicle = Vehiculo(**payload)
    session.add(vehicle)
    session.flush()
    _set_monthly_status(session, vehicle.id, estado_mensualidad)
    session.commit()
    session.refresh(vehicle)
    vehicle.estado_mensualidad = estado_mensualidad
    return vehicle


@database_operation
def list_vehicles(session: Session, offset: int, limit: int) -> dict:
    total = session.scalar(select(func.count()).select_from(Vehiculo))
    items = session.execute(
        text(
            """
            SELECT v.id, v.placa, v.color, v.modelo, v.marca, v.tipo, v.celda_id,
                   m.estado AS estado_mensualidad
            FROM vehiculo AS v
            LEFT JOIN LATERAL (
                SELECT estado
                FROM mensualidad
                WHERE id_vehiculo = v.id
                ORDER BY id_mensualidad DESC
                LIMIT 1
            ) AS m ON TRUE
            ORDER BY v.id
            OFFSET :offset LIMIT :limit
            """
        ),
        {"offset": offset, "limit": limit},
    ).mappings().all()
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@database_operation
def activate_monthly_status(session: Session, vehicle_id: int) -> dict:
    result = _set_monthly_status(session, vehicle_id, "activo")
    session.commit()
    return result


def _set_monthly_status(
    session: Session, vehicle_id: int, estado: EstadoMensualidad
) -> dict:
    vehicle = session.scalar(
        select(Vehiculo.id).where(Vehiculo.id == vehicle_id).with_for_update()
    )
    if vehicle is None:
        raise VehiculoError(404, "Vehículo no encontrado.")

    # La tabla no tiene secuencia ni valor por defecto para su clave primaria.
    session.execute(text("LOCK TABLE mensualidad IN EXCLUSIVE MODE"))
    current = session.execute(
        text(
            """
            SELECT id_mensualidad
            FROM mensualidad
            WHERE id_vehiculo = :vehicle_id
            ORDER BY id_mensualidad DESC
            LIMIT 1
            FOR UPDATE
            """
        ),
        {"vehicle_id": vehicle_id},
    ).mappings().first()

    if current is None:
        monthly_id = session.scalar(
            text("SELECT COALESCE(MAX(id_mensualidad), 0) + 1 FROM mensualidad")
        )
        result = session.execute(
            text(
                """
                INSERT INTO mensualidad (id_mensualidad, estado, id_vehiculo)
                VALUES (:monthly_id, :estado, :vehicle_id)
                RETURNING id_mensualidad, id_vehiculo, estado
                """
            ),
            {"monthly_id": monthly_id, "estado": estado, "vehicle_id": vehicle_id},
        ).mappings().one()
    else:
        result = session.execute(
            text(
                """
                UPDATE mensualidad
                SET estado = :estado
                WHERE id_mensualidad = :monthly_id
                RETURNING id_mensualidad, id_vehiculo, estado
                """
            ),
            {"estado": estado, "monthly_id": current["id_mensualidad"]},
        ).mappings().one()
    return dict(result)


def _include_monthly_status(session: Session, vehicle: Vehiculo) -> Vehiculo:
    status = session.execute(
        text(
            """
            SELECT estado
            FROM mensualidad
            WHERE id_vehiculo = :vehicle_id
            ORDER BY id_mensualidad DESC
            LIMIT 1
            """
        ),
        {"vehicle_id": vehicle.id},
    ).scalar_one_or_none()
    vehicle.estado_mensualidad = status
    return vehicle


@database_operation
def get_vehicle(session: Session, vehicle_id: int) -> Vehiculo:
    return _include_monthly_status(session, find_vehicle(session, vehicle_id))


@database_operation
def update_vehicle(session: Session, vehicle_id: int, data: VehiculoActualizar) -> Vehiculo:
    vehicle = find_vehicle(session, vehicle_id)
    updates = data.model_dump(exclude_unset=True)
    estado_mensualidad = updates.pop("estado_mensualidad", None)
    for key, value in updates.items():
        setattr(vehicle, key, value)
    if estado_mensualidad is not None:
        _set_monthly_status(session, vehicle_id, estado_mensualidad)
    session.commit()
    session.refresh(vehicle)
    if estado_mensualidad is None:
        return _include_monthly_status(session, vehicle)
    vehicle.estado_mensualidad = estado_mensualidad
    return vehicle


@database_operation
def delete_vehicle(session: Session, vehicle_id: int) -> None:
    vehicle = find_vehicle(session, vehicle_id)
    session.delete(vehicle)
    session.commit()
