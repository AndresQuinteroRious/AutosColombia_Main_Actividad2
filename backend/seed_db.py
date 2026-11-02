"""Script para llenar la base de datos con datos de prueba realistas."""

import random
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import load_database_settings
from app.database import get_engine
from app.models import Celda, Novedad, Operador, Pago, Usuario, Vehiculo


def seed_celdas(session: Session) -> None:
    """Crear celdas de parqueadero."""
    celdas_data = []
    
    # Crear celdas para motos (A-01 a A-10)
    for i in range(1, 11):
        celdas_data.append({"codigo": f"A-{i:02d}", "tipo": "Moto"})
    
    # Crear celdas para automóviles (B-01 a B-10)
    for i in range(1, 11):
        celdas_data.append({"codigo": f"B-{i:02d}", "tipo": "Automóvil"})
    
    # Crear celdas para camionetas (C-01 a C-05)
    for i in range(1, 6):
        celdas_data.append({"codigo": f"C-{i:02d}", "tipo": "Camioneta"})
    
    # Crear celdas para furgones (D-01 a D-03)
    for i in range(1, 4):
        celdas_data.append({"codigo": f"D-{i:02d}", "tipo": "Furgón"})
    
    # Crear celdas para camiones (E-01 a E-02)
    for i in range(1, 3):
        celdas_data.append({"codigo": f"E-{i:02d}", "tipo": "Camión"})

    for data in celdas_data:
        existing = session.query(Celda).filter_by(codigo=data["codigo"]).first()
        if not existing:
            celda = Celda(**data)
            session.add(celda)
    
    session.flush()
    print(f"✓ Celdas creadas: {len(celdas_data)}")


def seed_operadores(session: Session) -> None:
    """Crear operadores del parqueadero."""
    operadores_data = [
        {"nombre": "Carlos Rodríguez", "telefono": "3101234567"},
        {"nombre": "María González", "telefono": "3209876543"},
        {"nombre": "Pedro Martínez", "telefono": "3154567890"},
    ]

    for data in operadores_data:
        existing = session.query(Operador).filter_by(nombre=data["nombre"]).first()
        if not existing:
            operador = Operador(**data)
            session.add(operador)
    
    session.flush()
    print(f"✓ Operadores creados: {len(operadores_data)}")


def seed_vehiculos(session: Session) -> None:
    """Crear vehículos de prueba."""
    # Obtener celdas existentes
    celdas = session.query(Celda).all()
    celda_map = {c.codigo: c.id for c in celdas}
    celda_ids = list(celda_map.values())

    # Datos para generar vehículos aleatorios
    colores = ["Rojo", "Azul", "Blanco", "Negro", "Gris", "Verde", "Amarillo", "Plateado", "Café", "Beige", "Dorado", "Naranja"]
    marcas_auto = ["Chevrolet", "Renault", "Mazda", "Toyota", "Honda", "Nissan", "Volkswagen", "Kia", "Hyundai", "Peugeot"]
    marcas_moto = ["Honda", "Yamaha", "Suzuki", "Bajaj", "AKT", "Kawasaki"]
    marcas_camioneta = ["Ford", "Chevrolet", "Toyota", "Nissan", "Mazda", "Jeep", "Mitsubishi"]
    marcas_furgon = ["Mercedes-Benz", "Ford", "Renault", "Peugeot", "Fiat"]
    marcas_camion = ["Volvo", "Scania", "Mercedes-Benz", "International", "MAN"]
    tipos = ["MOTO", "AUTOMOVIL", "CAMIONETA", "FURGON", "CAMION", "OTROS"]

    def generar_placa(index: int) -> str:
        """Generar una placa aleatoria colombiana."""
        letras = "ABCDEFHJKLMNPQRSTUVWXYZ"
        # Formato: 3 letras + 3 números
        placa = f"{random.choice(letras)}{random.choice(letras)}{random.choice(letras)}{random.randint(100, 999)}"
        return placa

    vehiculos_data = []
    for i in range(80):
        tipo = random.choice(tipos)
        
        if tipo == "MOTO":
            marca = random.choice(marcas_moto)
        elif tipo == "AUTOMOVIL":
            marca = random.choice(marcas_auto)
        elif tipo == "CAMIONETA":
            marca = random.choice(marcas_camioneta)
        elif tipo == "FURGON":
            marca = random.choice(marcas_furgon)
        elif tipo == "CAMION":
            marca = random.choice(marcas_camion)
        else:
            marca = random.choice(marcas_auto)
        
        vehiculo = {
            "placa": generar_placa(i),
            "color": random.choice(colores),
            "modelo": random.randint(2010, 2025),
            "marca": marca,
            "tipo": tipo,
            "celda_id": random.choice(celda_ids) if celda_ids else None,
        }
        vehiculos_data.append(vehiculo)

    for data in vehiculos_data:
        existing = session.query(Vehiculo).filter_by(placa=data["placa"]).first()
        if not existing:
            vehiculo = Vehiculo(**data)
            session.add(vehiculo)
    
    session.flush()
    print(f"✓ Vehículos creados: {len(vehiculos_data)}")


def seed_usuarios(session: Session) -> None:
    """Crear usuarios del sistema."""
    usuarios_data = [
        {
            "nombre": "Administrador Principal",
            "documento": "ADMIN-001",
            "telefono": "3001112222",
            "fecha_vencimiento": date(2035, 12, 31),
            "rol": "ADMINISTRADOR",
            "turno": "RESPALDO",
            "horas_semana": 42,
            "ausentismo_horas": 0,
        },
        {
            "nombre": "Empleado Turno Mañana",
            "documento": "EMP-001",
            "telefono": "3013334444",
            "fecha_vencimiento": date(2030, 6, 30),
            "rol": "EMPLEADO",
            "turno": "MAÑANA",
            "horas_semana": 42,
            "ausentismo_horas": 0,
        },
        {
            "nombre": "Empleado Turno Tarde",
            "documento": "EMP-002",
            "telefono": "3025556666",
            "fecha_vencimiento": date(2029, 1, 15),
            "rol": "EMPLEADO",
            "turno": "TARDE",
            "horas_semana": 42,
            "ausentismo_horas": 0,
        },
        {
            "nombre": "Empleado Turno Noche",
            "documento": "EMP-003",
            "telefono": "3037778888",
            "fecha_vencimiento": date(2029, 9, 30),
            "rol": "EMPLEADO",
            "turno": "NOCHE",
            "horas_semana": 42,
            "ausentismo_horas": 0,
        },
        {
            "nombre": "Empleado Turno Respaldo",
            "documento": "EMP-004",
            "telefono": "3049990000",
            "fecha_vencimiento": date(2028, 3, 31),
            "rol": "EMPLEADO",
            "turno": "RESPALDO",
            "horas_semana": 42,
            "ausentismo_horas": 0,
        },
    ]

    for data in usuarios_data:
        existing = session.query(Usuario).filter_by(documento=data["documento"]).first()
        if not existing:
            usuario = Usuario(**data)
            session.add(usuario)
    
    session.flush()
    print(f"✓ Usuarios creados: {len(usuarios_data)}")


def seed_novedades(session: Session) -> None:
    """Crear novedades/incidentes de prueba."""
    novedades_data = [
        {"descripcion": "Rayón en la puerta lateral izquierda"},
        {"descripcion": "Espejo retrovisor roto"},
        {"descripcion": "Llanta pinchada al ingreso"},
        {"descripcion": "Mancha de aceite en el asiento"},
        {"descripcion": "Faro delantero dañado"},
        {"descripcion": "Puerta trasera no cierra correctamente"},
        {"descripcion": "Aire acondicionado no funciona"},
        {"descripcion": "Radio del vehículo no enciende"},
    ]

    for data in novedades_data:
        novedad = Novedad(**data)
        session.add(novedad)
    
    session.flush()
    print(f"✓ Novedades creadas: {len(novedades_data)}")


def seed_pagos(session: Session) -> None:
    """Crear pagos de prueba."""
    pagos_data = [
        {"valor": Decimal("150000.00"), "periodo": "2025-01"},
        {"valor": Decimal("150000.00"), "periodo": "2025-02"},
        {"valor": Decimal("180000.00"), "periodo": "2025-01"},
        {"valor": Decimal("180000.00"), "periodo": "2025-02"},
        {"valor": Decimal("200000.00"), "periodo": "2025-01"},
        {"valor": Decimal("120000.00"), "periodo": "2025-01"},
        {"valor": Decimal("120000.00"), "periodo": "2025-02"},
        {"valor": Decimal("160000.00"), "periodo": "2025-01"},
        {"valor": Decimal("160000.00"), "periodo": "2025-02"},
        {"valor": Decimal("250000.00"), "periodo": "2025-01"},
    ]

    for data in pagos_data:
        pago = Pago(**data)
        session.add(pago)
    
    session.flush()
    print(f"✓ Pagos creados: {len(pagos_data)}")


def main() -> None:
    """Ejecutar el seeding de la base de datos."""
    print("Conectando a la base de datos...")
    settings = load_database_settings()
    engine = get_engine()
    
    print("Iniciando seeding de datos...")
    with Session(engine) as session:
        seed_celdas(session)
        seed_operadores(session)
        seed_vehiculos(session)
        seed_usuarios(session)
        seed_novedades(session)
        # seed_pagos(session)  # Comentado por solicitud del usuario
        
        session.commit()
    
    print("\n✓ Seeding completado exitosamente")


if __name__ == "__main__":
    main()
