from datetime import date
import base64
from unittest.mock import MagicMock

import pytest

from app.models import Operador, Usuario
from app.schemas.usuario import UsuarioCrear
from app.services.usuario import (
    UsuarioError,
    _hash_password,
    _verify_password,
    autenticar_usuario,
    cambiar_contrasena,
    create_user,
    obtener_usuario_por_token,
)
from app.services.estancia import ServicioEstancia


def test_create_user_creates_associated_operator_in_same_transaction():
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = None
    session.refresh.side_effect = lambda entity: setattr(entity, "id", 1)
    data = UsuarioCrear(
        nombre="Ana Pérez",
        documento="CC-123",
        telefono="3001234567",
        fecha_vencimiento=date(2030, 1, 1),
    )

    user = create_user(session, data)

    added = [call.args[0] for call in session.add.call_args_list]
    assert user in added
    operator = next(entity for entity in added if isinstance(entity, Operador))
    assert isinstance(user, Usuario)
    assert user.requiere_cambio_contrasena is True
    assert (operator.nombre, operator.telefono, operator.documento) == (
        user.nombre,
        user.telefono,
        user.documento,
    )
    session.commit.assert_called_once()


def test_create_user_allows_multiple_administrators():
    session = MagicMock()
    data = UsuarioCrear(
        nombre="Segundo administrador",
        documento="CC-456",
        telefono="3007654321",
        fecha_vencimiento=date(2030, 1, 1),
        rol="ADMINISTRADOR",
    )

    user = create_user(session, data)

    assert user.rol == "ADMINISTRADOR"
    session.commit.assert_called_once()


def test_password_is_hashed_and_used_after_first_change():
    session = MagicMock()
    user = Usuario(
        id=5,
        nombre="Ana Pérez",
        documento="CC-123",
        telefono="3001234567",
        fecha_vencimiento=date(2030, 1, 1),
        requiere_cambio_contrasena=True,
    )
    session.query.return_value.filter_by.return_value.first.return_value = user

    assert autenticar_usuario(session, "CC-123", "3001234567") is user
    with pytest.raises(UsuarioError):
        autenticar_usuario(session, "CC-123", "0000000000")

    cambiar_contrasena(session, user, "Una clave segura 2026")
    assert user.requiere_cambio_contrasena is False
    assert user.contrasena_hash is not None
    assert "Una clave segura 2026" not in user.contrasena_hash
    assert _verify_password("Una clave segura 2026", user.contrasena_hash)
    assert not _verify_password("Otra clave 2026", user.contrasena_hash)
    with pytest.raises(UsuarioError):
        autenticar_usuario(session, "CC-123", "3001234567")
    assert autenticar_usuario(session, "CC-123", "", "Una clave segura 2026") is user


def test_hash_usa_salt_diferente_para_cada_contrasena():
    first_hash = _hash_password("Una clave segura 2026")
    second_hash = _hash_password("Una clave segura 2026")
    assert first_hash != second_hash
    assert _verify_password("Una clave segura 2026", first_hash)


def test_token_de_usuario_pendiente_solo_permita_cambiar_contrasena():
    session = MagicMock()
    user = Usuario(
        id=5,
        nombre="Ana Pérez",
        documento="CC-123",
        telefono="3001234567",
        fecha_vencimiento=date(2030, 1, 1),
        requiere_cambio_contrasena=True,
    )
    session.get.return_value = user
    token = base64.urlsafe_b64encode(b"5:EMPLEADO:CC-123").decode("ascii")

    with pytest.raises(UsuarioError, match="cambiar tu contraseña"):
        obtener_usuario_por_token(session, token)
    assert obtener_usuario_por_token(session, token, permitir_cambio_contrasena=True) is user


def test_operador_actual_repara_usuario_existente_sin_operador():
    session = MagicMock()
    session.scalars.return_value = []
    session.scalar.return_value = None
    session.refresh.side_effect = lambda entity: setattr(entity, "id", 7)
    user = Usuario(
        nombre="Ana Pérez",
        documento="CC-123",
        telefono="3001234567",
        fecha_vencimiento=date(2030, 1, 1),
    )

    operator = ServicioEstancia(session).operador_actual(user)

    assert operator == {"id": 7, "nombre": "Ana Pérez", "telefono": "3001234567"}
    created = next(call.args[0] for call in session.add.call_args_list if isinstance(call.args[0], Operador))
    assert created.documento == "CC-123"
    session.commit.assert_called_once()
