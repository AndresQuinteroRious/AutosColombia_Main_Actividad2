from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Usuario
from app.schemas.celda import CeldaActualizar, CeldaCrear, CeldaRespuesta, CeldasPagina
from app.services import celda as service
from app.services import usuario as usuario_service

router = APIRouter(prefix="/celdas", tags=["Celdas"])
DatabaseSession = Annotated[Session, Depends(get_session)]
CellId = Annotated[int, Path(ge=1, le=9223372036854775807)]


def get_current_user(
    session: DatabaseSession,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> Usuario:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Se requiere un token de sesión válido.")
    token = authorization.split(" ", 1)[1].strip()
    return usuario_service.obtener_usuario_por_token(session, token)


def require_admin(usuario_actual: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario_actual.rol != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="Solo el administrador puede administrar celdas.")
    return usuario_actual


@router.post("", response_model=CeldaRespuesta, status_code=201)
def create(data: CeldaCrear, session: DatabaseSession, current_admin: Usuario = Depends(require_admin)):
    del current_admin
    return service.create_cell(session, data)


@router.get("", response_model=CeldasPagina)
def list_all(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: Usuario = Depends(get_current_user),
):
    del current_user
    return service.list_cells(session, offset, limit)


@router.get("/{id}", response_model=CeldaRespuesta)
def get_one(id: CellId, session: DatabaseSession, current_user: Usuario = Depends(get_current_user)):
    del current_user
    return service.get_cell(session, id)


@router.patch("/{id}", response_model=CeldaRespuesta)
def update(id: CellId, data: CeldaActualizar, session: DatabaseSession, current_admin: Usuario = Depends(require_admin)):
    del current_admin
    return service.update_cell(session, id, data)


@router.delete("/{id}", status_code=204)
def delete(id: CellId, session: DatabaseSession, current_admin: Usuario = Depends(require_admin)) -> Response:
    del current_admin
    service.delete_cell(session, id)
    return Response(status_code=204)

