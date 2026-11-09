from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Usuario
from app.routers.usuarios import get_current_user, require_admin
from app.schemas.novedad import (
    NovedadActualizar,
    NovedadCrear,
    NovedadHistorialItem,
    NovedadRespuesta,
    NovedadVehiculoCrear,
    NovedadesHistorialPagina,
    NovedadesPagina,
)
from app.services import novedad as service

router = APIRouter(prefix="/novedades", tags=["Novedades"])
DatabaseSession = Annotated[Session, Depends(get_session)]
NovedadId = Annotated[int, Path(ge=1, le=9223372036854775807)]


@router.post("", response_model=NovedadRespuesta, status_code=201)
def create(data: NovedadCrear, session: DatabaseSession):
    return service.create_novedad(session, data)


@router.post("/vehiculo", response_model=NovedadHistorialItem, status_code=201)
def create_for_vehicle(
    data: NovedadVehiculoCrear,
    session: DatabaseSession,
    current_user: Usuario = Depends(get_current_user),
):
    del current_user
    return service.create_vehicle_novedad(session, data)


@router.get("", response_model=NovedadesPagina)
def list_all(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return service.list_novedades(session, offset, limit)


@router.get("/historial", response_model=NovedadesHistorialPagina)
def vehicle_history(
    session: DatabaseSession,
    fecha_desde: Annotated[date | None, Query()] = None,
    fecha_hasta: Annotated[date | None, Query()] = None,
    placa: Annotated[str | None, Query(max_length=20)] = None,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    current_admin: Usuario = Depends(require_admin),
):
    del current_admin
    return service.list_vehicle_history(session, fecha_desde, fecha_hasta, placa, offset, limit)


@router.get("/{id}", response_model=NovedadRespuesta)
def get_one(id: NovedadId, session: DatabaseSession):
    return service.get_novedad(session, id)


@router.patch("/{id}", response_model=NovedadRespuesta)
def update(id: NovedadId, data: NovedadActualizar, session: DatabaseSession):
    return service.update_novedad(session, id, data)


@router.delete("/{id}", status_code=204)
def delete(id: NovedadId, session: DatabaseSession) -> Response:
    service.delete_novedad(session, id)
    return Response(status_code=204)
