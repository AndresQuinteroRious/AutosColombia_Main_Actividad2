# Diagrama de clases del backend

El diagrama representa las entidades SQLAlchemy definidas en `backend/app/models.py` y sus relaciones por claves foráneas. Las clases `*Crear`, `*Actualizar` y `*Respuesta` de `backend/app/schemas/` son contratos de la API y no entidades persistentes, por lo que no se incluyen.

```mermaid
classDiagram
    direction LR

    class Vehiculo {
        +int id
        +str placa
        +str color
        +int modelo
        +str marca
        +str tipo
        +int celda_id
        +Celda celda
        +validate_text(key, value) str
        +validate_modelo(key, value) int
    }

    class Celda {
        +int id
        +str codigo
        +str tipo
        +validate_text(key, value) str
    }

    class Estancia {
        +int id
        +int vehiculo_id
        +int celda_id
        +datetime entrada
        +datetime salida
        +int operador_entrada_id
        +int operador_salida_id
        +Vehiculo vehiculo
        +Celda celda
        +Operador operador_entrada
        +Operador operador_salida
        +esta_abierta() bool
        +cerrar(fecha_salida, operador) None
    }

    class Operador {
        +int id
        +str nombre
        +str telefono
        +str direccion
        +validate_text(key, value) str
    }

    class Usuario {
        +int id
        +str nombre
        +str documento
        +str telefono
        +date fecha_vencimiento
        +str rol
        +str turno
        +int horas_semana
        +int ausentismo_horas
        +validate_text(key, value) str
        +validate_rol(key, value) str
        +validate_turno(key, value) str
        +validate_horas(key, value) int
        +horas_disponibles() int
        +cobertura_semanal(usuarios)$ dict
        +mensualidad_vigente() bool
    }

    class Cuenta {
        +int id
        +str usuario
        +str password_hash
        +str rol
        +int operador_id
    }

    class Novedad {
        +int id
        +str descripcion
        +datetime fecha
        +validate_text(key, value) str
    }

    class Pago {
        +int id
        +Decimal valor
        +datetime fecha
        +str periodo
        +validate_text(key, value) str
        +validate_valor(key, value) Decimal
    }

    Celda "0..1" <-- "0..*" Vehiculo : asignación opcional
    Vehiculo "1" <-- "0..*" Estancia : vehículo
    Celda "1" <-- "0..*" Estancia : espacio ocupado
    Operador "1" <-- "0..*" Estancia : registra entrada
    Operador "0..1" <-- "0..*" Estancia : registra salida
    Operador "0..1" <-- "0..*" Cuenta : cuenta asociada
```

## Notas

- `Vehiculo.celda_id` admite `NULL`; cada vehículo tiene cero o una celda asignada. La restricción de estancia abierta evita asignar simultáneamente la misma celda abierta a varias estancias.
- Toda estancia referencia un vehículo, una celda y un operador de entrada. El operador de salida es opcional y se establece al cerrar la estancia.
- `Cuenta.operador_id` es una clave foránea opcional. El modelo no declara una relación ORM ni una restricción de unicidad para ese campo.
- `Usuario`, `Pago` y `Novedad` no tienen relaciones declaradas con otras entidades en el modelo actual.
- Las validaciones del diagrama son métodos ORM abreviados; los atributos opcionales o anulables corresponden a columnas que aceptan `NULL`.
