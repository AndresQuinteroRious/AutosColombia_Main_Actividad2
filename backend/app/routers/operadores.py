from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Operador, Usuario
from app.schemas.operador import OperadorActualizar, OperadorCrear, OperadorRespuesta, OperadoresPagina
from app.services import operador as service
from app.services import usuario as usuario_service

router = APIRouter(prefix="/operadores", tags=["Operadores"])
DatabaseSession = Annotated[Session, Depends(get_session)]
OperatorId = Annotated[int, Path(ge=1, le=9223372036854775807)]


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
        raise HTTPException(status_code=403, detail="Solo el administrador puede administrar empleados.")
    return usuario_actual


@router.post("", response_model=OperadorRespuesta, status_code=201)
def create(data: OperadorCrear, session: DatabaseSession, current_admin: Usuario = Depends(require_admin)) -> Operador:
    del current_admin
    return service.create_operator(session, data)


@router.get("", response_model=OperadoresPagina)
def list_all(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    del current_user
    return service.list_operators(session, offset, limit)


@router.get("/{id}", response_model=OperadorRespuesta)
def get_one(id: OperatorId, session: DatabaseSession, current_user: Usuario = Depends(get_current_user)) -> Operador:
    del current_user
    return service.get_operator(session, id)


@router.patch("/{id}", response_model=OperadorRespuesta)
def update(id: OperatorId, data: OperadorActualizar, session: DatabaseSession, current_admin: Usuario = Depends(require_admin)) -> Operador:
    del current_admin
    return service.update_operator(session, id, data)


@router.delete("/{id}", status_code=204)
def delete(id: OperatorId, session: DatabaseSession, current_admin: Usuario = Depends(require_admin)) -> Response:
    del current_admin
    service.delete_operator(session, id)
    return Response(status_code=204)

