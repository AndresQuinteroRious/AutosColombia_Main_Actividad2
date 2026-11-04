"""Router público para consultar el estado de ocupación de las celdas.

No requiere autenticación: la grilla de estado es información pública
que se muestra en la pantalla de inicio del sistema.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.celda_estado import CeldasEstadoRespuesta
from app.services.celda_estado import CeldaEstadoError, get_estado_celdas

router = APIRouter(prefix="/celdas", tags=["Celdas"])
DatabaseSession = Annotated[Session, Depends(get_session)]


@router.get("/estado", response_model=CeldasEstadoRespuesta)
def estado_celdas(session: DatabaseSession) -> CeldasEstadoRespuesta:
    """Devuelve todas las celdas con su estado de ocupación (público, sin autenticación)."""
    return get_estado_celdas(session)
