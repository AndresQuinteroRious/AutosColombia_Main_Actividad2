from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.estancia import (
    EntradaCrear, SalidaCrear, EstanciaRespuesta, EstanciaAbiertaListadoRespuesta,
    EstanciasPagina, EstadoVehiculoRespuesta,
)
from app.schemas.vehiculo import Placa
from app.services.estancia import ServicioEstancia

router = APIRouter(prefix="/estancias", tags=["Estancias"])
DatabaseSession = Annotated[Session, Depends(get_session)]
EntityId = Annotated[int, Query(ge=1, le=9223372036854775807)]
Offset = Annotated[int, Query(ge=0, le=9223372036854775807)]
Limit = Annotated[int, Query(ge=1, le=100)]


@router.post("/entrada", response_model=EstanciaRespuesta, status_code=201)
def entrada(data: EntradaCrear, session: DatabaseSession) -> EstanciaRespuesta:
    return ServicioEstancia(session).entrada(data)


@router.post("/salida", response_model=EstanciaRespuesta)
def salida(data: SalidaCrear, session: DatabaseSession) -> EstanciaRespuesta:
    return ServicioEstancia(session).salida(data)


@router.get("/vehiculo/{placa}", response_model=EstadoVehiculoRespuesta)
def consultar(placa: Placa, session: DatabaseSession) -> EstadoVehiculoRespuesta:
    return ServicioEstancia(session).consultar(placa)


@router.get("/abiertas", response_model=list[EstanciaAbiertaListadoRespuesta])
def abiertas(session: DatabaseSession) -> list[EstanciaAbiertaListadoRespuesta]:
    return ServicioEstancia(session).abiertas()


@router.get("/historial", response_model=EstanciasPagina)
def historial(
    session: DatabaseSession,
    placa: Placa | None = None,
    celda_id: EntityId | None = None,
    offset: Offset = 0,
    limit: Limit = 20,
) -> EstanciasPagina:
    return ServicioEstancia(session).historial(placa, celda_id, offset, limit)
