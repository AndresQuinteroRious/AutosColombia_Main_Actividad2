from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, field_validator

from app.models import required_text


Texto = Annotated[str, BeforeValidator(lambda value: required_text(value, "El campo"))]
Documento = Annotated[Texto, AfterValidator(str.upper)]
FechaVencimiento = Annotated[date, Field(ge=date(1900, 1, 1))]
RolUsuario = Annotated[str, BeforeValidator(lambda value: required_text(value, "El rol"))]
TurnoUsuario = Annotated[str, BeforeValidator(lambda value: required_text(value, "El turno"))]


class UsuarioCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Texto
    documento: Documento
    telefono: Texto
    fecha_vencimiento: FechaVencimiento
    rol: RolUsuario = "EMPLEADO"
    turno: TurnoUsuario = "MAÑANA"
    horas_semana: int = 42
    ausentismo_horas: int = 0

    @field_validator("rol")
    @classmethod
    def validate_rol(cls, value):
        if value is None:
            return None
        value = str(value).strip().upper()
        roles_validos = {"ADMINISTRADOR", "EMPLEADO"}
        if value not in roles_validos:
            raise ValueError("rol debe ser ADMINISTRADOR o EMPLEADO.")
        return value

    @field_validator("turno")
    @classmethod
    def validate_turno(cls, value):
        if value is None:
            return None
        value = str(value).strip().upper()
        turnos_validos = {"MAÑANA", "TARDE", "NOCHE", "RESPALDO"}
        if value not in turnos_validos:
            raise ValueError("turno debe ser MAÑANA, TARDE, NOCHE o RESPALDO.")
        return value

    @field_validator("horas_semana", "ausentismo_horas")
    @classmethod
    def validate_horas(cls, value, info):
        if value is None:
            return None
        valor = int(value)
        if info.field_name == "horas_semana" and not 1 <= valor <= 84:
            raise ValueError("horas_semana debe estar entre 1 y 84.")
        if info.field_name == "ausentismo_horas" and not 0 <= valor <= 84:
            raise ValueError("ausentismo_horas debe estar entre 0 y 84.")
        return valor


class UsuarioLogin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    documento: Documento
    telefono: Texto


class UsuarioActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Texto | None = None
    documento: Documento | None = None
    telefono: Texto | None = None
    fecha_vencimiento: FechaVencimiento | None = None
    rol: RolUsuario | None = None
    turno: TurnoUsuario | None = None
    horas_semana: int | None = None
    ausentismo_horas: int | None = None

    @field_validator("rol")
    @classmethod
    def validate_rol(cls, value):
        if value is None:
            return None
        value = str(value).strip().upper()
        roles_validos = {"ADMINISTRADOR", "EMPLEADO"}
        if value not in roles_validos:
            raise ValueError("rol debe ser ADMINISTRADOR o EMPLEADO.")
        return value

    @field_validator("turno")
    @classmethod
    def validate_turno(cls, value):
        if value is None:
            return None
        value = str(value).strip().upper()
        turnos_validos = {"MAÑANA", "TARDE", "NOCHE", "RESPALDO"}
        if value not in turnos_validos:
            raise ValueError("turno debe ser MAÑANA, TARDE, NOCHE o RESPALDO.")
        return value

    @field_validator("horas_semana", "ausentismo_horas")
    @classmethod
    def validate_horas(cls, value, info):
        if value is None:
            return None
        valor = int(value)
        if info.field_name == "horas_semana" and not 1 <= valor <= 84:
            raise ValueError("horas_semana debe estar entre 1 y 84.")
        if info.field_name == "ausentismo_horas" and not 0 <= valor <= 84:
            raise ValueError("ausentismo_horas debe estar entre 0 y 84.")
        return valor

    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Los campos enviados no pueden ser nulos.")
        return value


class UsuarioRespuesta(UsuarioCrear):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: int


class UsuarioLoginRespuesta(BaseModel):
    usuario: UsuarioRespuesta
    token: str
    rol: str
    permisos: list[str]


class UsuariosPagina(BaseModel):
    items: list[UsuarioRespuesta]
    total: int
    offset: int
    limit: int
