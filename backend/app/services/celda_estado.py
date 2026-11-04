"""Servicio para consultar el estado público de las celdas (libre / ocupada)."""

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Celda, Estancia, Vehiculo
from app.schemas.celda_estado import CeldaEstadoRespuesta, CeldasEstadoRespuesta, VehiculoEnCelda


class CeldaEstadoError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def get_estado_celdas(session: Session) -> CeldasEstadoRespuesta:
    """Devuelve todas las celdas con estado de ocupación.

    Una celda se considera ocupada cuando tiene una estancia abierta
    (salida IS NULL) o cuando tiene un vehículo asignado directamente
    mediante vehiculo.celda_id. Las estancias abiertas tienen prioridad
    porque reflejan el estado operacional actual del sistema de control.
    """
    try:
        # Estancias abiertas → celda_id → vehiculo
        estancias_abiertas = (
            select(Estancia.celda_id, Vehiculo)
            .join(Vehiculo, Vehiculo.id == Estancia.vehiculo_id)
            .where(Estancia.salida.is_(None))
        )
        estancias_rows = session.execute(estancias_abiertas).all()
        # {celda_id: Vehiculo} para estancias abiertas
        ocupadas_por_estancia: dict[int, Vehiculo] = {
            row.celda_id: row[1] for row in estancias_rows
        }

        # Vehículos asignados directamente mediante celda_id
        vehiculos_por_celda: dict[int, Vehiculo] = {
            v.celda_id: v
            for v in session.scalars(
                select(Vehiculo).where(Vehiculo.celda_id.is_not(None))
            )
            if v.celda_id not in ocupadas_por_estancia
        }

        # Todas las celdas ordenadas alfabéticamente por código
        celdas = list(session.scalars(select(Celda).order_by(Celda.codigo)))

        items: list[CeldaEstadoRespuesta] = []
        for celda in celdas:
            vehiculo_obj = ocupadas_por_estancia.get(celda.id) or vehiculos_por_celda.get(celda.id)
            vehiculo_info: VehiculoEnCelda | None = None
            if vehiculo_obj is not None:
                vehiculo_info = VehiculoEnCelda(
                    placa=vehiculo_obj.placa,
                    marca=vehiculo_obj.marca,
                    modelo=vehiculo_obj.modelo,
                    color=vehiculo_obj.color,
                    tipo=vehiculo_obj.tipo,
                )
            items.append(
                CeldaEstadoRespuesta(
                    id=celda.id,
                    codigo=celda.codigo,
                    tipo=celda.tipo,
                    ocupada=vehiculo_info is not None,
                    vehiculo=vehiculo_info,
                )
            )

        libres = sum(1 for c in items if not c.ocupada)
        return CeldasEstadoRespuesta(
            items=items,
            total=len(items),
            libres=libres,
            ocupadas=len(items) - libres,
        )
    except SQLAlchemyError:
        raise CeldaEstadoError(503, "No se pudo consultar el estado de las celdas.") from None
