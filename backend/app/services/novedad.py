from datetime import date, datetime, time, timedelta
from functools import wraps
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Novedad, Vehiculo
from app.schemas.novedad import (
    NovedadActualizar,
    NovedadCrear,
    NovedadHistorialItem,
    NovedadVehiculoCrear,
)


class NovedadError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


BOGOTA = ZoneInfo("America/Bogota")


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
                raise NovedadError(409, "La novedad tiene registros relacionados y no se puede eliminar.") from None
            if code in {"23502", "23514"}:
                raise NovedadError(422, "Los datos incumplen las restricciones de la novedad.") from None
            raise NovedadError(409, "La operación entra en conflicto con los datos existentes.") from None
        except SQLAlchemyError:
            session.rollback()
            raise NovedadError(
                503,
                "No se pudo completar la operación de novedades. Verifica que PostgreSQL esté disponible y que la migración novedad_vehiculo esté aplicada.",
            ) from None
    return wrapped


def find_novedad(session: Session, novedad_id: int) -> Novedad:
    novedad = session.get(Novedad, novedad_id)
    if novedad is None:
        raise NovedadError(404, "Novedad no encontrada.")
    return novedad


@database_operation
def create_novedad(session: Session, data: NovedadCrear) -> Novedad:
    novedad = Novedad(**data.model_dump())
    session.add(novedad)
    session.commit()
    session.refresh(novedad)
    return novedad


@database_operation
def create_vehicle_novedad(session: Session, data: NovedadVehiculoCrear) -> NovedadHistorialItem:
    vehiculo = session.get(Vehiculo, data.vehiculo_id)
    if vehiculo is None:
        raise NovedadError(404, "Vehículo no encontrado.")
    novedad = Novedad(
        vehiculo_id=vehiculo.id,
        descripcion=data.descripcion,
    )
    session.add(novedad)
    session.commit()
    session.refresh(novedad)
    return NovedadHistorialItem(
        id=novedad.id,
        placa=vehiculo.placa,
        descripcion=novedad.descripcion,
        fecha=novedad.fecha,
    )


@database_operation
def list_novedades(session: Session, offset: int, limit: int) -> dict:
    total = session.scalar(select(func.count()).select_from(Novedad))
    items = list(session.scalars(select(Novedad).order_by(Novedad.id).offset(offset).limit(limit)))
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@database_operation
def list_vehicle_history(
    session: Session,
    fecha_desde: date | None,
    fecha_hasta: date | None,
    placa: str | None,
    offset: int,
    limit: int,
) -> dict:
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise NovedadError(422, "La fecha desde no puede ser posterior a la fecha hasta.")

    condiciones = []
    if fecha_desde:
        desde = datetime.combine(fecha_desde, time.min, tzinfo=BOGOTA)
        condiciones.append(Novedad.fecha >= desde.astimezone(timezone.utc))
    if fecha_hasta:
        hasta_exclusivo = datetime.combine(
            fecha_hasta + timedelta(days=1), time.min, tzinfo=BOGOTA
        )
        condiciones.append(Novedad.fecha < hasta_exclusivo.astimezone(timezone.utc))
    placa_normalizada = placa.strip().upper() if placa and placa.strip() else None
    if placa_normalizada:
        condiciones.append(func.upper(Vehiculo.placa).contains(placa_normalizada, autoescape=True))

    total = session.scalar(
        select(func.count())
        .select_from(Novedad)
        .outerjoin(Vehiculo, Vehiculo.id == Novedad.vehiculo_id)
        .where(*condiciones)
    )
    rows = session.execute(
        select(
            Novedad.id,
            Vehiculo.placa.label("placa"),
            Novedad.descripcion,
            Novedad.fecha,
        )
        .outerjoin(Vehiculo, Vehiculo.id == Novedad.vehiculo_id)
        .where(*condiciones)
        .order_by(Novedad.fecha.desc(), Novedad.id.desc())
        .offset(offset)
        .limit(limit)
    ).mappings().all()
    return {
        "items": [NovedadHistorialItem(**dict(row)) for row in rows],
        "total": total or 0,
        "offset": offset,
        "limit": limit,
    }


@database_operation
def get_novedad(session: Session, novedad_id: int) -> Novedad:
    return find_novedad(session, novedad_id)


@database_operation
def update_novedad(session: Session, novedad_id: int, data: NovedadActualizar) -> Novedad:
    novedad = find_novedad(session, novedad_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(novedad, key, value)
    session.commit()
    session.refresh(novedad)
    return novedad


@database_operation
def delete_novedad(session: Session, novedad_id: int) -> None:
    novedad = find_novedad(session, novedad_id)
    session.delete(novedad)
    session.commit()
