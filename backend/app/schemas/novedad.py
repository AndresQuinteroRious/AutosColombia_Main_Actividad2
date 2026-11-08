from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.models import required_text


Texto = Annotated[str, BeforeValidator(lambda value: required_text(value, "El campo"))]


class NovedadCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    descripcion: Texto


class NovedadActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    descripcion: Texto | None = None

    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Los campos enviados no pueden ser nulos.")
        return value


class NovedadRespuesta(NovedadCrear):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: int
    fecha: datetime


class NovedadVehiculoCrear(NovedadCrear):
    vehiculo_id: Annotated[int, Field(strict=True, ge=1, le=9223372036854775807)]
    fecha: date


class NovedadHistorialItem(BaseModel):
    id: int
    placa: str | None
    descripcion: str
    fecha: datetime


class NovedadesHistorialPagina(BaseModel):
    items: list[NovedadHistorialItem]
    total: int
    offset: int
    limit: int


class NovedadesPagina(BaseModel):
    items: list[NovedadRespuesta]
    total: int
    offset: int
    limit: int
