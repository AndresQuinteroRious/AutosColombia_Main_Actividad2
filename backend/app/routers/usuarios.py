from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Usuario
from app.schemas.usuario import (
    CambioContrasena,
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioLogin,
    UsuarioLoginRespuesta,
    UsuarioRespuesta,
    UsuariosPagina,
)
from app.services import usuario as service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
DatabaseSession = Annotated[Session, Depends(get_session)]
UserId = Annotated[int, Path(ge=1, le=9223372036854775807)]


def get_current_user(
    session: DatabaseSession,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> Usuario:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Se requiere un token de sesión válido.")
    token = authorization.split(" ", 1)[1].strip()
    return service.obtener_usuario_por_token(session, token)


def require_admin(usuario_actual: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario_actual.rol != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="Solo el administrador puede realizar esta acción.")
    return usuario_actual


@router.post("/login", response_model=UsuarioLoginRespuesta)
def login(data: UsuarioLogin, session: DatabaseSession):
    usuario = service.autenticar_usuario(session, data.documento, data.telefono, data.contrasena)
    token = service.crear_token_usuario(usuario)
    permisos = list(service.permisos_del_rol(usuario.rol).keys())
    return {
        "usuario": UsuarioRespuesta.model_validate(usuario),
        "token": token,
        "rol": usuario.rol,
        "permisos": permisos,
        "requiere_cambio_contrasena": usuario.requiere_cambio_contrasena,
    }


@router.post("/cambiar-contrasena")
def change_password(
    data: CambioContrasena,
    session: DatabaseSession,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Se requiere un token de sesión válido.")
    token = authorization.split(" ", 1)[1].strip()
    user = service.obtener_usuario_por_token(session, token, permitir_cambio_contrasena=True)
    service.cambiar_contrasena(session, user, data.contrasena)
    return {"status": "ok"}


@router.post("", response_model=UsuarioRespuesta, status_code=201)
def create(data: UsuarioCrear, session: DatabaseSession, current_admin: Usuario = Depends(require_admin)):
    del current_admin
    return service.create_user(session, data)


@router.get("", response_model=UsuariosPagina)
def list_all(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_admin: Usuario = Depends(require_admin),
):
    del current_admin
    return service.list_users(session, offset, limit)


@router.get("/cobertura-semanal")
def cobertura_semanal(session: DatabaseSession):
    return service.get_cobertura_semanal(session)


@router.get("/{id}", response_model=UsuarioRespuesta)
def get_one(id: UserId, session: DatabaseSession, current_user: Usuario = Depends(get_current_user)):
    del current_user
    return service.get_user(session, id)


@router.patch("/{id}", response_model=UsuarioRespuesta)
def update(id: UserId, data: UsuarioActualizar, session: DatabaseSession, current_admin: Usuario = Depends(require_admin)):
    del current_admin
    return service.update_user(session, id, data)


@router.delete("/{id}", status_code=204)
def delete(id: UserId, session: DatabaseSession, current_user: Usuario = Depends(get_current_user)) -> Response:
    if current_user.rol != "ADMINISTRADOR" and current_user.id != id:
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar usuarios.")
    service.delete_user(session, id)
    return Response(status_code=204)
