from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Usuario
from app.schemas.celda import CeldaRespuesta
from app.schemas.estancia import (
    EntradaCrear,
    EstanciaRespuesta,
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


@router.post("/salida", response_model=EstanciaRespuesta)
def salida(data: SalidaCrear, session: DatabaseSession) -> EstanciaRespuesta:
    return ServicioEstancia(session).salida(data)


@router.get("/vehiculo/{placa}", response_model=EstadoVehiculoRespuesta)
def consultar(placa: Placa, session: DatabaseSession) -> EstadoVehiculoRespuesta:
    return ServicioEstancia(session).consultar(placa)
