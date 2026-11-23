from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_serializer, field_validator

from app.models import required_text


Texto = Annotated[str, BeforeValidator(lambda value: required_text(value, "El campo"))]
ValorPago = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
VehiculoId = Annotated[int, Field(gt=0, le=9223372036854775807)]


class PagoCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valor: ValorPago
    periodo: Texto | None = None
    vehiculo_id: VehiculoId


class PagoActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valor: ValorPago | None = None
    periodo: Texto | None = None
    vehiculo_id: VehiculoId | None = None

    @field_validator("valor", "periodo", "vehiculo_id")
    @classmethod
    def reject_null(cls, value: Decimal | str | int | None) -> Decimal | str | int:
        if value is None:
            raise ValueError("Los campos enviados no pueden ser nulos.")
        return value


class PagoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: int
    fecha: datetime
    valor: ValorPago
    periodo: Texto
    vehiculo_id: VehiculoId | None
    placa: str | None


class PlacaPago(BaseModel):
    id: int
    placa: str
    tipo: str
    tarifa: float | None
    tiene_pago: bool
    pago_activo: bool


class TarifasPago(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    automovil: ValorPago
    motocicleta: ValorPago

    @field_serializer("automovil", "motocicleta", when_used="json")
    def serialize_amount(self, value: Decimal) -> float:
        return float(value)


class PagosPagina(BaseModel):
    items: list[PagoRespuesta]
    total: int
    offset: int
    limit: int
