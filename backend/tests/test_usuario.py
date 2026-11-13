from datetime import date
from unittest.mock import MagicMock

from app.models import Operador, Usuario
from app.schemas.usuario import UsuarioCrear
from app.services.usuario import create_user
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
    assert (operator.nombre, operator.telefono, operator.documento) == (
        user.nombre,
        user.telefono,
        user.documento,
    )
    session.commit.assert_called_once()


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
