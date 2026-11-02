"""Modelos iniciales. Importar este módulo no crea tablas ni abre conexiones."""

import decimal
from datetime import datetime, timezone

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Identity, Index, Integer, Numeric, Text, UniqueConstraint, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, validates


class Base(DeclarativeBase):
    pass


def required_text(value: str, attribute: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{attribute} debe ser texto no vacío.")
    return value.strip()


class Vehiculo(Base):
    __tablename__ = "vehiculo"
    __table_args__ = (
        UniqueConstraint("placa", name="uq_vehiculo_placa"),
        CheckConstraint("placa ~ '[^[:space:]]'", name="ck_vehiculo_placa_no_vacia"),
        CheckConstraint("placa = upper(regexp_replace(placa, '^[[:space:]]+|[[:space:]]+$', '', 'g'))", name="ck_vehiculo_placa_normalizada"),
        CheckConstraint("color ~ '[^[:space:]]'", name="ck_vehiculo_color_no_vacio"),
        CheckConstraint("marca ~ '[^[:space:]]'", name="ck_vehiculo_marca_no_vacia"),
        CheckConstraint("modelo BETWEEN 1 AND 9999", name="ck_vehiculo_modelo_anio"),
        CheckConstraint("tipo IN ('MOTO', 'AUTOMOVIL', 'CAMIONETA', 'FURGON', 'CAMION', 'OTROS')", name="ck_vehiculo_tipo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    placa: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(Text, nullable=False)
    modelo: Mapped[int] = mapped_column(Integer, nullable=False)
    marca: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)
    celda_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("celda.id", name="fk_vehiculo_celda", ondelete="SET NULL"), nullable=True
    )

    @validates("placa", "color", "marca", "tipo")
    def validate_text(self, key: str, value: str) -> str:
        value = required_text(value, key)
        if key == "placa":
            return value.upper()
        if key == "tipo" and value not in {"MOTO", "AUTOMOVIL", "CAMIONETA", "FURGON", "CAMION", "OTROS"}:
            raise ValueError("tipo debe ser MOTO, AUTOMOVIL, CAMIONETA, FURGON, CAMION u OTROS.")
        return value

    @validates("modelo")
    def validate_modelo(self, key: str, value: int) -> int:
        if type(value) is not int or not 1 <= value <= 9999:
            raise ValueError("modelo debe ser un año entero entre 1 y 9999.")
        return value

    celda: Mapped["Celda"] = relationship()


class Celda(Base):
    __tablename__ = "celda"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_celda_codigo"),
        CheckConstraint("codigo ~ '[^[:space:]]'", name="ck_celda_codigo_no_vacio"),
        CheckConstraint("codigo = upper(regexp_replace(codigo, '^[[:space:]]+|[[:space:]]+$', '', 'g'))", name="ck_celda_codigo_normalizado"),
        CheckConstraint("tipo ~ '[^[:space:]]'", name="ck_celda_tipo_no_vacio"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)

    @validates("codigo", "tipo")
    def validate_text(self, key: str, value: str) -> str:
        value = required_text(value, key)
        return value.upper() if key == "codigo" else value


class Operador(Base):
    __tablename__ = "operador"
    __table_args__ = (
        CheckConstraint("nombre ~ '[^[:space:]]'", name="ck_operador_nombre_no_vacio"),
        CheckConstraint("telefono ~ '[^[:space:]]'", name="ck_operador_telefono_no_vacio"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    telefono: Mapped[str] = mapped_column(Text, nullable=False)
    direccion: Mapped[str] = mapped_column(Text, nullable=True)

    @validates("nombre", "telefono")
    def validate_text(self, key: str, value: str) -> str:
        return required_text(value, key)


class Estancia(Base):
    __tablename__ = "estancia"
    __table_args__ = (
        CheckConstraint("salida >= entrada", name="ck_estancia_orden_fechas"),
        CheckConstraint(
            "(salida IS NULL) = (operador_salida_id IS NULL)",
            name="ck_estancia_cierre_completo",
        ),
        Index("uq_estancia_vehiculo_abierta", "vehiculo_id", unique=True,
              postgresql_where=text("salida IS NULL")),
        Index("uq_estancia_celda_abierta", "celda_id", unique=True,
              postgresql_where=text("salida IS NULL")),
        Index("ix_estancia_vehiculo_entrada", "vehiculo_id", "entrada"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    vehiculo_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("vehiculo.id", name="fk_estancia_vehiculo", ondelete="RESTRICT"), nullable=False
    )
    celda_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("celda.id", name="fk_estancia_celda", ondelete="RESTRICT"), nullable=False
    )
    entrada: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    salida: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    operador_entrada_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("operador.id", name="fk_estancia_operador_entrada", ondelete="RESTRICT"), nullable=False
    )
    operador_salida_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("operador.id", name="fk_estancia_operador_salida", ondelete="RESTRICT"), nullable=True
    )

    vehiculo: Mapped[Vehiculo] = relationship()
    celda: Mapped[Celda] = relationship()
    operador_entrada: Mapped[Operador] = relationship(foreign_keys=[operador_entrada_id])
    operador_salida: Mapped[Operador | None] = relationship(foreign_keys=[operador_salida_id])

    def esta_abierta(self) -> bool:
        return self.salida is None

    def cerrar(self, fecha_salida: datetime, operador: Operador) -> None:
        """Valida y asigna el cierre; el servicio debe gestionar flush y commit."""
        if not self.esta_abierta():
            raise ValueError("La estancia ya está cerrada.")
        if not isinstance(fecha_salida, datetime) or fecha_salida.utcoffset() is None:
            raise ValueError("La fecha de salida debe tener zona horaria.")
        if not isinstance(self.entrada, datetime) or self.entrada.utcoffset() is None:
            raise ValueError("La entrada debe estar cargada y tener zona horaria antes de cerrar.")
        if fecha_salida.astimezone(timezone.utc) < self.entrada.astimezone(timezone.utc):
            raise ValueError("La salida no puede ser anterior a la entrada.")
        if not isinstance(operador, Operador) or operador.id is None:
            raise ValueError("El operador de salida debe tener un id asignado.")
        self.salida = fecha_salida
        self.operador_salida = operador
        self.operador_salida_id = operador.id


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        UniqueConstraint("documento", name="uq_usuario_documento"),
        CheckConstraint("nombre ~ '[^[:space:]]'", name="ck_usuario_nombre_no_vacio"),
        CheckConstraint("documento ~ '[^[:space:]]'", name="ck_usuario_documento_no_vacio"),
        CheckConstraint("telefono ~ '[^[:space:]]'", name="ck_usuario_telefono_no_vacio"),
        CheckConstraint("rol IN ('ADMINISTRADOR', 'EMPLEADO')", name="ck_usuario_rol_valido"),
        CheckConstraint("turno IN ('MAÑANA', 'TARDE', 'NOCHE', 'RESPALDO')", name="ck_usuario_turno_valido"),
        CheckConstraint("horas_semana BETWEEN 1 AND 84", name="ck_usuario_horas_semana_valida"),
        CheckConstraint("ausentismo_horas BETWEEN 0 AND 84", name="ck_usuario_ausentismo_horas_valida"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    documento: Mapped[str] = mapped_column(Text, nullable=False)
    telefono: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_vencimiento: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    rol: Mapped[str] = mapped_column(Text, nullable=False, default="EMPLEADO")
    turno: Mapped[str] = mapped_column(Text, nullable=False, default="MAÑANA")
    horas_semana: Mapped[int] = mapped_column(Integer, nullable=False, default=42)
    ausentismo_horas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    @validates("nombre", "documento", "telefono")
    def validate_text(self, key: str, value: str) -> str:
        return required_text(value, key)

    @validates("rol")
    def validate_rol(self, key: str, value: str) -> str:
        normalized = required_text(value, key).upper()
        roles_validos = {"ADMINISTRADOR", "EMPLEADO"}
        if normalized not in roles_validos:
            raise ValueError("rol debe ser ADMINISTRADOR o EMPLEADO.")
        return normalized

    @validates("turno")
    def validate_turno(self, key: str, value: str) -> str:
        normalized = required_text(value, key).upper()
        turnos_validos = {"MAÑANA", "TARDE", "NOCHE", "RESPALDO"}
        if normalized not in turnos_validos:
            raise ValueError("turno debe ser MAÑANA, TARDE, NOCHE o RESPALDO.")
        return normalized

    @validates("horas_semana", "ausentismo_horas")
    def validate_horas(self, key: str, value: int) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{key} debe ser un entero.")
        if key == "horas_semana" and not 1 <= value <= 84:
            raise ValueError("horas_semana debe estar entre 1 y 84 horas.")
        if key == "ausentismo_horas" and not 0 <= value <= 84:
            raise ValueError("ausentismo_horas debe estar entre 0 y 84 horas.")
        return value

    def horas_disponibles(self) -> int:
        return max(0, self.horas_semana - self.ausentismo_horas)

    @staticmethod
    def cobertura_semanal(usuarios: list["Usuario"]) -> dict:
        empleados = [usuario for usuario in usuarios if usuario.rol == "EMPLEADO"]
        total_programado = sum(usuario.horas_semana for usuario in empleados)
        total_disponible = sum(usuario.horas_disponibles() for usuario in empleados)
        total_requerido = 168
        faltante_horas = max(0, total_requerido - total_disponible)
        cobertura_pct = (total_disponible / total_requerido * 100) if total_requerido else 0
        return {
            "total_requerido": total_requerido,
            "total_programado": total_programado,
            "total_disponible": total_disponible,
            "faltante_horas": faltante_horas,
            "cobertura_pct": round(cobertura_pct, 2),
            "sin_huecos": faltante_horas == 0,
        }

    def mensualidad_vigente(self) -> bool:
        """Verifica si la mensualidad está vigente basándose en la fecha de vencimiento."""
        from datetime import date
        return self.fecha_vencimiento >= date.today()


class Novedad(Base):
    __tablename__ = "novedad"
    __table_args__ = (
        CheckConstraint("descripcion ~ '[^[:space:]]'", name="ck_novedad_descripcion_no_vacio"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @validates("descripcion")
    def validate_text(self, key: str, value: str) -> str:
        return required_text(value, key)


class Pago(Base):
    __tablename__ = "pago"
    __table_args__ = (
        CheckConstraint("valor > 0", name="ck_pago_valor_positivo"),
        CheckConstraint("periodo ~ '[^[:space:]]'", name="ck_pago_periodo_no_vacio"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    valor: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    periodo: Mapped[str] = mapped_column(Text, nullable=False)

    @validates("periodo")
    def validate_text(self, key: str, value: str) -> str:
        return required_text(value, key)

    @validates("valor")
    def validate_valor(self, key: str, value: decimal.Decimal) -> decimal.Decimal:
        if not isinstance(value, (int, float, decimal.Decimal)):
            raise ValueError("valor debe ser un número.")
        valor_decimal = decimal.Decimal(str(value))
        if valor_decimal <= 0:
            raise ValueError("valor debe ser mayor que 0.")
        return valor_decimal

# models.py
class Cuenta(Base):
    __tablename__ = "cuenta"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    usuario: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    rol: Mapped[str] = mapped_column(Text, nullable=False)
    operador_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("operador.id"), nullable=True)