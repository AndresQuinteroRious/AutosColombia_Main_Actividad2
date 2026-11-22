from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.models import required_text


Texto = Annotated[str, BeforeValidator(lambda value: required_text(value, "El campo"))]


class NovedadCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    descripcion: Texto
    id_estancia: Annotated[int, Field(strict=True, ge=1, le=9223372036854775807)]


class NovedadActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    descripcion: Texto | None = None

    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Los campos enviados no pueden ser nulos.")
        return value


class NovedadRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: int
    descripcion: str
    fecha: datetime
    id_estancia: int | None = None


class NovedadVehiculoCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")
    descripcion: Texto
    vehiculo_id: Annotated[int, Field(strict=True, ge=1, le=9223372036854775807)]


class NovedadHistorialItem(BaseModel):
    id: int
    placa: str | None
    descripcion: str
    fecha: datetime
    id_estancia: int | None = None
    entrada: datetime | None = None
    salida: datetime | None = None
    celda: str | None = None


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
