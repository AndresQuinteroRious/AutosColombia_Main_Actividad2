import base64
import hashlib
import hmac
import secrets
from functools import wraps

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Operador, Usuario
from app.schemas.usuario import UsuarioActualizar, UsuarioCrear


class UsuarioError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


PERMISOS_POR_ROL = {
    "ADMINISTRADOR": {
        "gestionar_usuarios": False,
        "gestionar_turnos": True,
        "registrar_ausentismos": True,
        "cambiar_roles": False,
        "editar_celdas": True,
        "eliminar_celdas": True,
        "editar_empleados": False,
        "gestionar_operadores": True,
    },
    "EMPLEADO": {
        "gestionar_usuarios": False,
        "gestionar_turnos": True,
        "registrar_ausentismos": True,
        "cambiar_roles": False,
        "editar_celdas": False,
        "eliminar_celdas": False,
        "editar_empleados": False,
        "gestionar_operadores": False,
    },
}


def permisos_del_rol(rol: str) -> dict[str, bool]:
    rol_normalizado = str(rol or "").strip().upper()
    permisos = PERMISOS_POR_ROL.get(rol_normalizado)
    if permisos is None:
        raise UsuarioError(422, "El rol del usuario no es válido.")
    return permisos


def calcular_cobertura_semanal(usuarios: list[Usuario]) -> dict:
    """Asegura cobertura de 168 horas por semana para evitar huecos en la operación."""
    total_requerido = 168
    empleados = [usuario for usuario in usuarios if usuario.rol == "EMPLEADO"]
    total_programado = sum(usuario.horas_semana for usuario in empleados)
    total_disponible = sum(usuario.horas_disponibles() for usuario in empleados)
    faltante_horas = max(0, total_requerido - total_disponible)
    return {
        "total_requerido": total_requerido,
        "total_programado": total_programado,
        "total_disponible": total_disponible,
        "faltante_horas": faltante_horas,
        "cobertura_pct": round((total_disponible / total_requerido) * 100, 2) if total_requerido else 0,
        "sin_huecos": faltante_horas == 0,
    }


def validar_permiso_rol(rol: str, accion: str) -> None:
    """Garantiza reglas básicas de acceso por rol para el control de acceso."""
    permisos = permisos_del_rol(rol)
    if not permisos.get(accion, False):
        raise UsuarioError(403, "Este rol no tiene permisos para esa acción.")


def crear_token_usuario(usuario: Usuario) -> str:
    payload = f"{usuario.id}:{usuario.rol}:{usuario.documento}"
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii")


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
            if code == "23505" and constraint == "uq_usuario_documento":
                raise UsuarioError(409, "Ya existe un usuario con ese documento.") from None
            if code == "23503":
                raise UsuarioError(409, "El usuario tiene registros relacionados y no se puede eliminar.") from None
            if code in {"23502", "23514"}:
                raise UsuarioError(422, "Los datos incumplen las restricciones del usuario.") from None
            raise UsuarioError(409, "La operación entra en conflicto con los datos existentes.") from None
        except SQLAlchemyError:
            session.rollback()
            raise UsuarioError(503, "No se pudo completar la operación con la base de datos.") from None
    return wrapped


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "scrypt":
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


@database_operation
def autenticar_usuario(
    session: Session,
    documento: str,
    telefono: str | None,
    contrasena: str | None = None,
) -> Usuario:
    documento_normalizado = str(documento or "").strip()
    telefono_normalizado = str(telefono or "").strip()
    usuario = session.query(Usuario).filter_by(documento=documento_normalizado).first()
    if usuario is None:
        raise UsuarioError(401, "Credenciales inválidas. Verifica el documento y el teléfono.")
    if usuario.contrasena_hash:
        credencial_valida = bool(contrasena) and _verify_password(contrasena, usuario.contrasena_hash)
    else:
        credencial_valida = bool(telefono_normalizado) and hmac.compare_digest(
            usuario.telefono, telefono_normalizado
        )
    if not credencial_valida:
        raise UsuarioError(401, "Credenciales inválidas. Verifica el documento y la contraseña o teléfono.")
    return usuario


def obtener_usuario_por_token(session: Session, token: str, permitir_cambio_contrasena: bool = False) -> Usuario:
    if not token:
        raise UsuarioError(401, "Falta el token de sesión.")
    token_ajustado = token + ("=" * (-len(token) % 4))
    try:
        payload = base64.urlsafe_b64decode(token_ajustado.encode("ascii")).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        raise UsuarioError(401, "El token de sesión es inválido.") from None

    try:
        usuario_id, _, _ = payload.split(":", 2)
    except ValueError as exc:
        raise UsuarioError(401, "El token de sesión es inválido.") from exc

    usuario = session.get(Usuario, int(usuario_id))
    if usuario is None:
        raise UsuarioError(401, "La sesión del usuario no existe o expiró.")
    if usuario.requiere_cambio_contrasena and not permitir_cambio_contrasena:
        raise UsuarioError(403, "Debes cambiar tu contraseña antes de continuar.")
    return usuario


@database_operation
def cambiar_contrasena(session: Session, usuario: Usuario, contrasena: str) -> Usuario:
    usuario.contrasena_hash = _hash_password(contrasena)
    usuario.requiere_cambio_contrasena = False
    session.commit()
    session.refresh(usuario)
    return usuario


@database_operation
def ensure_default_admin(session: Session) -> Usuario:
    usuario = session.query(Usuario).filter_by(documento="ADMIN-001").first()
    if usuario is not None:
        return usuario

    administrador = Usuario(
        nombre="Administrador Principal",
        documento="ADMIN-001",
        telefono="3001112222",
        fecha_vencimiento="2035-12-31",
        rol="ADMINISTRADOR",
        turno="RESPALDO",
        horas_semana=42,
        ausentismo_horas=0,
    )
    session.add(administrador)
    session.commit()
    session.refresh(administrador)
    return administrador

def find_user(session: Session, user_id: int) -> Usuario:
    user = session.get(Usuario, user_id)
    if user is None:
        raise UsuarioError(404, "Usuario no encontrado.")
    return user


@database_operation
def get_cobertura_semanal(session: Session) -> dict:
    usuarios = list(session.scalars(select(Usuario)).all())
    return calcular_cobertura_semanal(usuarios)


@database_operation
def create_user(session: Session, data: UsuarioCrear) -> Usuario:
    user = Usuario(**data.model_dump())
    user.requiere_cambio_contrasena = True
    session.add(user)
    session.add(Operador(
        nombre=user.nombre,
        telefono=user.telefono,
        documento=user.documento,
    ))
    session.commit()
    session.refresh(user)
    return user


@database_operation
def list_users(session: Session, offset: int, limit: int) -> dict:
    total = session.scalar(select(func.count()).select_from(Usuario))
    items = list(session.scalars(select(Usuario).order_by(Usuario.id).offset(offset).limit(limit)))
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@database_operation
def get_user(session: Session, user_id: int) -> Usuario:
    return find_user(session, user_id)


@database_operation
def update_user(session: Session, user_id: int, data: UsuarioActualizar) -> Usuario:
    user = find_user(session, user_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    session.commit()
    session.refresh(user)
    return user


@database_operation
def delete_user(session: Session, user_id: int) -> None:
    user = find_user(session, user_id)
    session.delete(user)
    session.commit()
