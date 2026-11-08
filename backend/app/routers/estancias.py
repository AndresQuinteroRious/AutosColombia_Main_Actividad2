from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Usuario
from app.schemas.celda import CeldaRespuesta
from app.schemas.estancia import (
    EntradaCrear,
    EstanciaRespuesta,
    EstanciasHistorialPagina,
    EstadoVehiculoRespuesta,
    OperadorEntradaRespuesta,
    SalidaCrear,
)
from app.schemas.vehiculo import Placa
from app.services.estancia import ServicioEstancia
from app.services import usuario as usuario_service

router = APIRouter(prefix="/estancias", tags=["Estancias"])
DatabaseSession = Annotated[Session, Depends(get_session)]


def usuario_actual(
    session: DatabaseSession,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> Usuario:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Se requiere un token de sesión válido.")
    token = authorization.split(" ", 1)[1].strip()
    return usuario_service.obtener_usuario_por_token(session, token)


@router.post("/entrada", response_model=EstanciaRespuesta, status_code=201)
def entrada(data: EntradaCrear, session: DatabaseSession) -> EstanciaRespuesta:
    return ServicioEstancia(session).entrada(data)


@router.get("/operador-actual", response_model=OperadorEntradaRespuesta)
def operador_actual(
    session: DatabaseSession,
    user: Usuario = Depends(usuario_actual),
) -> dict:
    return ServicioEstancia(session).operador_actual(user.documento)


@router.get("/celdas-disponibles", response_model=list[CeldaRespuesta])
def celdas_disponibles(
    session: DatabaseSession,
    user: Usuario = Depends(usuario_actual),
) -> list[CeldaRespuesta]:
    del user
    return ServicioEstancia(session).celdas_disponibles()


@router.get("/historial", response_model=EstanciasHistorialPagina)
def historial(
    session: DatabaseSession,
    fecha_desde: Annotated[date | None, Query()] = None,
    fecha_hasta: Annotated[date | None, Query()] = None,
    placa: Annotated[str | None, Query(max_length=20)] = None,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> EstanciasHistorialPagina:
    return ServicioEstancia(session).historial(fecha_desde, fecha_hasta, placa, offset, limit)


@router.post("/salida", response_model=EstanciaRespuesta)
def salida(data: SalidaCrear, session: DatabaseSession) -> EstanciaRespuesta:
    return ServicioEstancia(session).salida(data)


@router.get("/vehiculo/{placa}", response_model=EstadoVehiculoRespuesta)
def consultar(placa: Placa, session: DatabaseSession) -> EstadoVehiculoRespuesta:
    return ServicioEstancia(session).consultar(placa)
