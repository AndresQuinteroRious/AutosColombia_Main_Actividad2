from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import ConfigurationError
from app.database import get_engine
from app.models import Usuario
from app.routers.vehiculos import router as vehiculos_router
from app.services.vehiculo import VehiculoError
from app.routers.celdas import router as celdas_router
from app.services.celda import CeldaError
from app.routers.celda_estado import router as celda_estado_router
from app.services.celda_estado import CeldaEstadoError
from app.routers.operadores import router as operadores_router
from app.services.operador import OperadorError
from app.routers.estancias import router as estancias_router
from app.services.estancia import EstanciaError
from app.routers.usuarios import router as usuarios_router
from app.services.usuario import UsuarioError, ensure_default_admin
from app.routers.novedades import router as novedades_router
from app.services.novedad import NovedadError
from app.routers.pagos import router as pagos_router
from app.services.pago import PagoError

app = FastAPI(title="Autos Colombia API")


@app.on_event("startup")
def ensure_admin_account() -> None:
    try:
        with Session(get_engine()) as session:
            ensure_default_admin(session)
    except (ConfigurationError, SQLAlchemyError, OSError, RuntimeError, UsuarioError) as exc:
        print(
            "Advertencia: no se pudo crear el usuario administrador al iniciar. "
            "Verifica backend/.env y que PostgreSQL esté activo. "
            f"Detalle: {exc}"
        )


# El router de celda_estado se registra antes que celdas para que
# GET /celdas/estado no sea interceptado por GET /celdas/{id}.
app.include_router(celda_estado_router)
app.include_router(vehiculos_router)
app.include_router(celdas_router)
app.include_router(operadores_router)
app.include_router(estancias_router)
app.include_router(usuarios_router)
app.include_router(novedades_router)
app.include_router(pagos_router)


@app.exception_handler(VehiculoError)
@app.exception_handler(CeldaError)
@app.exception_handler(CeldaEstadoError)
@app.exception_handler(OperadorError)
@app.exception_handler(EstanciaError)
@app.exception_handler(UsuarioError)
@app.exception_handler(NovedadError)
@app.exception_handler(PagoError)
async def entity_error_handler(request, error: VehiculoError | CeldaError | CeldaEstadoError | OperadorError | EstanciaError | UsuarioError | NovedadError | PagoError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
