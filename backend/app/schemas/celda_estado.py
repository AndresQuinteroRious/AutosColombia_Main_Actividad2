"""Esquema de respuesta para el estado público de celdas (libre / ocupada)."""

from __future__ import annotations

from pydantic import BaseModel


class VehiculoEnCelda(BaseModel):
    """Información pública del vehículo que ocupa la celda."""

    placa: str
    marca: str
    modelo: int
    color: str
    tipo: str


class CeldaEstadoRespuesta(BaseModel):
    """Estado de una celda: datos básicos más si está ocupada y por qué vehículo."""

    id: int
    codigo: str
    tipo: str
    ocupada: bool
    vehiculo: VehiculoEnCelda | None = None


class CeldasEstadoRespuesta(BaseModel):
    """Lista completa de celdas con su estado de ocupación."""

    items: list[CeldaEstadoRespuesta]
    total: int
    libres: int
    ocupadas: int
