from datetime import date, datetime, time, timedelta, timezone
from functools import wraps
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from app.models import Celda, Estancia, Operador, Usuario, Vehiculo, required_text
from app.schemas.celda import CeldaRespuesta
from app.schemas.estancia import (
    EntradaCrear, SalidaCrear, EstanciaRespuesta, EstanciaAbiertaRespuesta,
    EstadoVehiculoRespuesta, EstanciasHistorialPagina, EstanciaAbiertaDetalle,
)
from app.schemas.vehiculo import VehiculoRespuesta


class EstanciaError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


BOGOTA = ZoneInfo("America/Bogota")


def transaccion(operation):
    """Una transacción por solicitud; materializa la respuesta antes del commit."""
    @wraps(operation)
    def wrapped(self, *args, **kwargs):
        try:
            with self.session.begin():
                return operation(self, *args, **kwargs)
        except IntegrityError as error:
            self.session.rollback()
            code = getattr(error.orig, "sqlstate", None)
            constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
            if code == "23505":
                if constraint == "uq_estancia_vehiculo_abierta":
                    raise EstanciaError(409, "El vehículo ya está dentro.") from None
                if constraint == "uq_estancia_celda_abierta":
                    raise EstanciaError(409, "La celda está ocupada.") from None
            if code == "23503":
                raise EstanciaError(404, "Una de las referencias ya no existe. Actualiza los datos.") from None
            if code in {"23502", "23514"}:
                raise EstanciaError(422, "Los datos incumplen las restricciones de la estancia.") from None
            raise EstanciaError(409, "La operación entra en conflicto con los datos existentes.") from None
        except SQLAlchemyError:
            self.session.rollback()
            raise EstanciaError(503, "No se pudo completar la operación con la base de datos.") from None
    return wrapped


class ServicioEstancia:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _vehiculo(self, placa: str) -> Vehiculo:
        vehiculo = self.session.scalar(select(Vehiculo).where(Vehiculo.placa == placa))
        if vehiculo is None:
            raise EstanciaError(404, "Vehículo no encontrado.")
        return vehiculo

    def _operador(self, operador_id: int) -> Operador:
        operador = self.session.get(Operador, operador_id)
        if operador is None:
            raise EstanciaError(404, "Operador no encontrado.")
        return operador

    def operador_actual(self, usuario: Usuario) -> dict:
        documento = usuario.documento.strip().upper()
        operadores = list(self.session.scalars(
            select(Operador)
            .where(func.upper(func.btrim(Operador.documento)) == documento)
            .order_by(Operador.id)
            .limit(2)
        ))
        if len(operadores) > 1:
            raise EstanciaError(409, "El usuario tiene más de un operador asociado; revisa sus datos.")
        if operadores:
            operador = operadores[0]
        else:
            # Vincula usuarios anteriores al cambio y crea el operador si aún no existe.
            operador = self.session.scalar(
                select(Operador).where(
                    func.upper(func.btrim(Operador.nombre)) == usuario.nombre.strip().upper(),
                    Operador.telefono == usuario.telefono,
                    Operador.documento.is_(None),
                ).order_by(Operador.id).limit(1)
            )
            if operador is None:
                operador = Operador(nombre=usuario.nombre, telefono=usuario.telefono)
                self.session.add(operador)
            operador.documento = documento
            try:
                self.session.commit()
                self.session.refresh(operador)
            except IntegrityError:
                self.session.rollback()
                operador = self.session.scalar(
                    select(Operador).where(func.upper(func.btrim(Operador.documento)) == documento)
                )
                if operador is None:
                    raise EstanciaError(409, "No se pudo asociar un operador al usuario.") from None
        return {"id": operador.id, "nombre": operador.nombre, "telefono": operador.telefono}

    def celdas_disponibles(self) -> list[Celda]:
        abiertas = select(Estancia.id).where(
            Estancia.celda_id == Celda.id,
            Estancia.salida.is_(None),
        )
        return list(
            self.session.scalars(
                select(Celda).where(~abiertas.exists()).order_by(Celda.id)
            )
        )

    @transaccion
    def abiertas(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        placa: str | None = None,
    ) -> list[EstanciaAbiertaDetalle]:
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise EstanciaError(422, "La fecha desde no puede ser posterior a la fecha hasta.")

        condiciones = [Estancia.salida.is_(None)]
        if fecha_desde:
            desde = datetime.combine(fecha_desde, time.min, tzinfo=BOGOTA)
            condiciones.append(Estancia.entrada >= desde.astimezone(timezone.utc))
        if fecha_hasta:
            hasta_exclusivo = datetime.combine(
                fecha_hasta + timedelta(days=1), time.min, tzinfo=BOGOTA
            )
            condiciones.append(Estancia.entrada < hasta_exclusivo.astimezone(timezone.utc))
        placa_normalizada = placa.strip().upper() if placa and placa.strip() else None
        if placa_normalizada:
            condiciones.append(Vehiculo.placa.contains(placa_normalizada, autoescape=True))

        rows = self.session.execute(
            select(
                Estancia.id,
                Vehiculo.placa.label("placa"),
                Vehiculo.marca.label("marca"),
                Vehiculo.modelo.label("modelo"),
                Vehiculo.color.label("color"),
                Vehiculo.tipo.label("tipo"),
                Celda.codigo.label("celda"),
                Estancia.entrada,
                Operador.nombre.label("operador_entrada"),
            )
            .join(Vehiculo, Vehiculo.id == Estancia.vehiculo_id)
            .join(Celda, Celda.id == Estancia.celda_id)
            .join(Operador, Operador.id == Estancia.operador_entrada_id)
            .where(*condiciones)
            .order_by(Estancia.entrada.desc(), Estancia.id.desc())
        ).mappings().all()
        return [EstanciaAbiertaDetalle(**dict(row)) for row in rows]

    @transaccion
    def historial(
        self,
        fecha_desde: date | None,
        fecha_hasta: date | None,
        placa: str | None,
        offset: int,
        limit: int,
        estado: str | None = None,
    ) -> EstanciasHistorialPagina:
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise EstanciaError(422, "La fecha desde no puede ser posterior a la fecha hasta.")

        condiciones = []
        if fecha_desde:
            desde = datetime.combine(fecha_desde, time.min, tzinfo=BOGOTA)
            condiciones.append(Estancia.entrada >= desde.astimezone(timezone.utc))
        if fecha_hasta:
            hasta_exclusivo = datetime.combine(
                fecha_hasta + timedelta(days=1), time.min, tzinfo=BOGOTA
            )
            condiciones.append(Estancia.entrada < hasta_exclusivo.astimezone(timezone.utc))
        placa_normalizada = placa.strip().upper() if placa and placa.strip() else None
        if placa_normalizada:
            condiciones.append(Vehiculo.placa.contains(placa_normalizada, autoescape=True))
        if estado == "ABIERTAS":
            condiciones.append(Estancia.salida.is_(None))
        elif estado == "CERRADAS":
            condiciones.append(Estancia.salida.is_not(None))

        total = self.session.scalar(
            select(func.count())
            .select_from(Estancia)
            .join(Vehiculo, Vehiculo.id == Estancia.vehiculo_id)
            .where(*condiciones)
        )
        operador_entrada = aliased(Operador)
        operador_salida = aliased(Operador)
        rows = self.session.execute(
            select(
                Estancia.id,
                Vehiculo.placa.label("placa"),
                Celda.codigo.label("celda"),
                operador_entrada.nombre.label("operador_entrada"),
                operador_salida.nombre.label("operador_salida"),
                Estancia.entrada,
                Estancia.salida,
            )
            .join(Vehiculo, Vehiculo.id == Estancia.vehiculo_id)
            .join(Celda, Celda.id == Estancia.celda_id)
            .join(operador_entrada, operador_entrada.id == Estancia.operador_entrada_id)
            .outerjoin(operador_salida, operador_salida.id == Estancia.operador_salida_id)
            .where(*condiciones)
            .order_by(Estancia.entrada.desc(), Estancia.id.desc())
            .offset(offset)
            .limit(limit)
        ).mappings().all()
        return EstanciasHistorialPagina(
            items=[dict(row) for row in rows],
            total=total or 0,
            offset=offset,
            limit=limit,
        )

    @transaccion
    def entrada(self, data: EntradaCrear) -> EstanciaRespuesta:
        vehiculo = self._vehiculo(data.placa)
        estado_mensualidad = self.session.scalar(
            text(
                """
                SELECT estado
                FROM mensualidad
                WHERE id_vehiculo = :vehiculo_id
                ORDER BY id_mensualidad DESC
                LIMIT 1
                """
            ),
            {"vehiculo_id": vehiculo.id},
        )
        if estado_mensualidad != "activo":
            raise EstanciaError(
                409,
                "La mensualidad de este vehículo no está activa; no se puede registrar la entrada.",
            )
        celda = self.session.get(Celda, data.celda_id)
        if celda is None:
            raise EstanciaError(404, "Celda no encontrada.")
        operador = self._operador(data.operador_id)
        if self.session.scalar(select(Estancia.id).where(
            Estancia.vehiculo_id == vehiculo.id, Estancia.salida.is_(None)
        )) is not None:
            raise EstanciaError(409, "El vehículo ya está dentro.")
        if self.session.scalar(select(Estancia.id).where(
            Estancia.celda_id == celda.id, Estancia.salida.is_(None)
        )) is not None:
            raise EstanciaError(409, "La celda está ocupada.")
        estancia = Estancia(vehiculo_id=vehiculo.id, celda_id=celda.id,
                            operador_entrada_id=operador.id, entrada=datetime.now(timezone.utc))
        self.session.add(estancia)
        # Los índices únicos deciden también cuando dos solicitudes superan las consultas previas.
        self.session.flush()
        return EstanciaRespuesta.model_validate(estancia)

    @transaccion
    def salida(self, data: SalidaCrear) -> EstanciaRespuesta:
        vehiculo = self._vehiculo(data.placa)
        operador = self._operador(data.operador_id)
        # PostgreSQL vuelve a evaluar salida IS NULL tras esperar el bloqueo.
        estancia = self.session.scalar(select(Estancia).where(
            Estancia.vehiculo_id == vehiculo.id, Estancia.salida.is_(None)
        ).with_for_update())
        if estancia is None:
            raise EstanciaError(409, "El vehículo no tiene una estancia abierta.")
        try:
            estancia.cerrar(datetime.now(timezone.utc), operador)
        except ValueError:
            raise EstanciaError(409, "No se puede cerrar la estancia con su estado o fecha actuales.") from None
        self.session.flush()
        return EstanciaRespuesta.model_validate(estancia)

    @transaccion
    def consultar(self, placa: str) -> EstadoVehiculoRespuesta:
        placa = required_text(placa, "placa").upper()
        # Una sola consulta da un estado consistente de vehículo, estancia y celda.
        row = self.session.execute(select(Vehiculo, Estancia, Celda).outerjoin(
            Estancia, and_(Estancia.vehiculo_id == Vehiculo.id, Estancia.salida.is_(None))
        ).outerjoin(Celda, Celda.id == Estancia.celda_id).where(Vehiculo.placa == placa)).one_or_none()
        if row is None:
            raise EstanciaError(404, "Vehículo no encontrado.")
        vehiculo, estancia, celda = row
        abierta = None
        if estancia is not None:
            abierta = EstanciaAbiertaRespuesta(
                **EstanciaRespuesta.model_validate(estancia).model_dump(),
                celda=CeldaRespuesta.model_validate(celda),
            )
        return EstadoVehiculoRespuesta(vehiculo=VehiculoRespuesta.model_validate(vehiculo),
                                       esta_dentro=estancia is not None, estancia=abierta)
