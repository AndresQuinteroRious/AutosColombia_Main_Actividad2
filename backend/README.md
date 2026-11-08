# Backend de Autos Colombia

## CRUD de operadores

Disponible únicamente en la API bajo `/operadores`, con POST, GET paginado,
GET por id, PATCH parcial y DELETE. Reutiliza el modelo y la tabla `operador`
de `0001`, cuya existencia y restricciones se comprobaron antes de implementar.
No se modificaron tablas, migraciones ni Angular.

Consulta el [README principal](../README.md#crud-de-operadores-solo-backend)
para contratos, reglas, ejemplo de `/docs`, comandos PowerShell del entorno
virtual existente, resultados comprobados y verificaciones pendientes.

## Gestión de celdas

Se revisó PostgreSQL antes de implementar el CRUD: la tabla `celda` y la revisión
`0001` ya existían y no había migraciones pendientes. Se verificaron `id BIGINT
GENERATED ALWAYS AS IDENTITY`, clave primaria, `codigo` único, campos `NOT NULL`
y los CHECK de código normalizado y textos no vacíos. No se modificaron migraciones
aplicadas ni se recrearon tablas.

El CRUD sigue la organización de vehículos: `app/schemas/celda.py`,
`app/services/celda.py` y `app/routers/celdas.py`.

| Operación | Resultado |
| --- | --- |
| POST `/celdas` con `codigo` y `tipo` | 201 con la celda creada |
| GET `/celdas?offset=0&limit=20` | 200 con items, total, offset y limit |
| GET `/celdas/{id}` | 200 o 404 |
| PATCH `/celdas/{id}` | 200; solo campos enviados, sin id ni valores nulos |
| DELETE `/celdas/{id}` | 204 sin cuerpo |

`codigo` se recorta y convierte a mayúsculas. `tipo` es texto libre obligatorio,
sin categorías ni compatibilidades con vehículos. Blancos y datos inválidos
devuelven 422; código duplicado y conflictos de relaciones devuelven 409, con
rollback. No se borran registros relacionados. Usa `/docs`, sección **Celdas**,
con un ejemplo como `{"codigo":"A-01","tipo":"Espacio general"}`.

Las pruebas `tests/test_celdas_postgres.py` se habilitan con `RUN_POSTGRES_TESTS=1`,
igual que las de vehículos. Verifican restricciones y CRUD reales dentro de
transacciones revertidas; las secuencias pueden avanzar. No ejecutan DDL.

Desde `backend`, en PowerShell:

```powershell
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini current
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini heads
$env:RUN_POSTGRES_TESTS = '1'
try {
    .\.venv\Scripts\python.exe -m pytest -q
} finally {
    Remove-Item Env:RUN_POSTGRES_TESTS -ErrorAction SilentlyContinue
}
```

Entorno verificado: Python 3.13.16 en Windows.
Ejecuta los siguientes comandos desde la carpeta `backend` en PowerShell.

## Preparar el entorno

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` fija todas las dependencias de ejecución y pruebas, incluidas
las transitivas. No es necesario activar el entorno virtual.

## Ejecutar la API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

`GET http://127.0.0.1:8000/health` devuelve `{"status": "ok"}` con estado HTTP 200.
La documentación interactiva está en `http://127.0.0.1:8000/docs`.

## Ejecutar las pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## PostgreSQL local

1. Instala e inicia PostgreSQL localmente y prepara una base de datos y un usuario.
   Este proyecto no instala PostgreSQL ni crea bases de datos. Las tablas se crean
   únicamente cuando ejecutas explícitamente las migraciones descritas más abajo.
2. Si no existe `.env`, copia la plantilla sin sobrescribir un archivo existente:

   ```powershell
   if (-not (Test-Path -LiteralPath .env)) {
       Copy-Item -LiteralPath .env.example -Destination .env
   }
   ```

3. Edita `.env` localmente. Completa `DB_NAME`, `DB_USER` y `DB_PASSWORD`.
   Confirma `DB_HOST` y `DB_PORT` (ejemplos: `127.0.0.1` y `5432`).
   `DB_CONNECT_TIMEOUT` es un entero entre 1 y 60 segundos.
   Los valores `CAMBIAR_...` son marcadores: no permiten intentar una conexión.
   Si la contraseña contiene espacios o `#`, usa comillas simples en `.env`.
   No se interpolan expresiones `${...}` dentro de los valores.
4. Comprueba la conexión:

   ```powershell
   .\.venv\Scripts\python.exe .\check_db.py
   $LASTEXITCODE
   ```

El comando solo ejecuta `SELECT 1`, sin crear ni modificar tablas. Devuelve 0
únicamente tras verificar una respuesta real; 2 si faltan variables o son
inválidas; 1 si la conexión o la consulta fallan. No imprime credenciales, URL
de conexión ni detalles del controlador que pudieran contener datos privados.

Desde cualquier carpeta puedes usar rutas absolutas:

```powershell
& 'C:\Users\user\Documents\IU DIGITAL\Clase Ingeniería de Software\AutosColombia\backend\.venv\Scripts\python.exe' 'C:\Users\user\Documents\IU DIGITAL\Clase Ingeniería de Software\AutosColombia\backend\check_db.py'
```

`app/config.py` localiza `.env` respecto a su propio archivo, independientemente
de la carpeta de ejecución. Las variables de entorno tienen prioridad sobre
`.env`. Reinicia los procesos después de cambiar la configuración.

`app/database.py` proporciona `get_engine()` y la dependencia `get_session()`
para futuros endpoints. No conecta al importar ni ejecuta `create_all` o
migraciones. `/health` sigue comprobando la API, no PostgreSQL, y funciona sin
configurar la base de datos. Las pruebas usan datos ficticios y conexiones
simuladas; la verificación real se hace con `check_db.py`.

`.env` está excluido de Git. `.env.example` se conserva como plantilla pública;
nunca copies contraseñas reales a ella.

## Modelos y migración inicial

Los modelos están en `app/models.py`, separados de la conexión (`app/database.py`)
y de la configuración (`app/config.py`). La revisión `0001`, en
`migrations/versions/0001_modelos_iniciales.py`, crea estas tablas:

| Clase | Tabla | Atributos |
| --- | --- | --- |
| Vehiculo | vehiculo | id, placa, color, modelo, marca, tipo |
| Celda | celda | id, codigo, tipo |
| Operador | operador | id, nombre, telefono |

- `id` usa `BIGINT GENERATED ALWAYS AS IDENTITY` y clave primaria. Se omite al insertar.
- Todos los campos son `NOT NULL`. Los textos tienen comprobaciones contra valores
  vacíos o formados únicamente por espacios, tabulaciones o saltos de línea.
- El ORM elimina espacios exteriores y convierte `placa` y `codigo` a mayúsculas,
  tanto al construir objetos como al asignar estos atributos. PostgreSQL exige
  esa forma normalizada mediante `CHECK` y garantiza su unicidad con `UNIQUE`.
  SQL directo y operaciones masivas que omiten validadores deben normalizar antes;
  la base rechaza valores sin normalizar en lugar de transformarlos silenciosamente.
- `modelo` es un año entero entre 1 y 9999, no un nombre comercial; no se impone
  un límite vinculado al año actual. `telefono` es texto y conserva prefijos y ceros.
- El tipo de vehículo admite únicamente `MOTO`, `AUTOMOVIL` y `CAMIONETA`.
  El tipo de celda es texto no vacío, sin catálogo ni reglas de compatibilidad todavía.
- No hay relaciones ni Estancia ni creación automática de tablas al iniciar
  FastAPI. `/health` conserva su funcionamiento independiente.

Al preparar esta revisión no se encontraron tablas de usuario ni revisiones
anteriores. Al implementar el CRUD se verificó que la revisión **0001 ya estaba
aplicada en autos_colombia**; no se modificó ni se volvió a aplicar.
Alembic reutiliza `backend/.env` y no almacena una URL con credenciales en su INI.

### Instalar y revisar sin modificar PostgreSQL

```powershell
Set-Location -LiteralPath 'C:\Users\user\Documents\IU DIGITAL\Clase Ingeniería de Software\AutosColombia\backend'
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe .\check_db.py
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini history
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini heads
Get-Content -LiteralPath .\migrations\versions\0001_modelos_iniciales.py
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini upgrade head --sql
```

El último comando **solo imprime SQL**: no conecta a PostgreSQL ni aplica cambios.
Incluye las tres tablas y `alembic_version`, que Alembic utiliza para registrar
las revisiones aplicadas. Las pruebas comparan modelos y migración y compilan
DDL PostgreSQL, pero no crean tablas ni prueban inserciones reales en la base local.

### Aplicar después de revisar (estos comandos sí modifican el esquema)

Ejecuta este bloque únicamente cuando decidas aplicar la migración:

```powershell
Set-Location -LiteralPath 'C:\Users\user\Documents\IU DIGITAL\Clase Ingeniería de Software\AutosColombia\backend'
.\.venv\Scripts\python.exe .\check_db.py
if ($LASTEXITCODE -ne 0) { throw 'La conexión no está disponible; no aplicar migraciones.' }
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) { throw 'La migración no se completó; revisar el esquema antes de continuar.' }
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini current
```

El resultado esperado de `current` después de aplicar es `0001 (head)`.
No uses `stamp` para dar por aplicada una migración que no se ejecutó. Si ya hay
tablas con los mismos nombres, detente y revisa su estructura: esta migración no
las borra ni las recrea y fallará ante un conflicto. Su `downgrade` elimina las
tres tablas y sus datos; no lo ejecutes como parte de la instalación.

Los paths de Alembic se resuelven respecto a `alembic.ini`. Desde otra carpeta,
utiliza rutas absolutas para el intérprete y `-c`, igual que con `check_db.py`.

## CRUD de usuarios

Disponible en la API bajo `/usuarios`, con POST, GET paginado, GET por id,
PATCH parcial y DELETE. Reutiliza el modelo `Usuario` y la tabla `usuario`
creada en la migración `68a8a3380d1d`.

| Operación | Resultado |
| --- | --- |
| POST `/usuarios` | 201 con el usuario creado, incluido su id |
| GET `/usuarios?offset=0&limit=20` | 200 con items, total, offset y limit |
| GET `/usuarios/{id}` | 200 o 404 |
| PATCH `/usuarios/{id}` | 200; solo campos enviados, sin id ni valores nulos |
| DELETE `/usuarios/{id}` | 204 sin cuerpo |

Al crear se requieren nombre, documento, telefono y fecha_vencimiento.
El documento se convierte a mayúsculas y debe ser único.
La fecha de vencimiento debe ser mayor o igual a 1900-01-01.
Los textos no pueden estar vacíos.

PATCH aplica solo los campos enviados, rechaza valores nulos y campos desconocidos.
Un documento duplicado devuelve 409, un usuario inexistente devuelve 404.
La unicidad se comprueba en PostgreSQL; las transacciones fallidas se revierten.

### Modelo Usuario

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| id | BIGINT | PRIMARY KEY, IDENTITY |
| nombre | TEXT | NOT NULL, no vacío |
| documento | TEXT | NOT NULL, UNIQUE, no vacío, mayúsculas |
| telefono | TEXT | NOT NULL, no vacío |
| fecha_vencimiento | DATE | NOT NULL, >= 1900-01-01 |

### Método mensualidad_vigente()

El modelo incluye un método `mensualidad_vigente()` que devuelve `True` si la
fecha de vencimiento es mayor o igual a la fecha actual.

## CRUD de novedades

Disponible en la API bajo `/novedades`, con POST, GET paginado, GET por id,
PATCH parcial y DELETE. Reutiliza el modelo `Novedad` y la tabla `novedad`
creada en la migración `68a8a3380d1d`.

| Operación | Resultado |
| --- | --- |
| POST `/novedades` | 201 con la novedad creada, incluido su id |
| GET `/novedades?offset=0&limit=20` | 200 con items, total, offset y limit |
| GET `/novedades/{id}` | 200 o 404 |
| PATCH `/novedades/{id}` | 200; solo campos enviados, sin id ni valores nulos |
| DELETE `/novedades/{id}` | 204 sin cuerpo |

Al crear se requiere descripcion. La fecha se asigna automáticamente con la
fecha y hora actual. Los textos no pueden estar vacíos.

PATCH aplica solo los campos enviados, rechaza valores nulos y campos desconocidos.
Una novedad inexistente devuelve 404.

### Modelo Novedad

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| id | BIGINT | PRIMARY KEY, IDENTITY |
| descripcion | TEXT | NOT NULL, no vacío |
| fecha | DATETIME (timezone) | NOT NULL, valor por defecto: now() |

## CRUD de pagos

Disponible en la API bajo `/pagos`, con POST, GET paginado, GET por id,
PATCH parcial y DELETE. Reutiliza el modelo `Pago` y la tabla `pago`
creada en la migración `68a8a3380d1d`.

| Operación | Resultado |
| --- | --- |
| POST `/pagos` | 201 con el pago creado, incluido su id |
| GET `/pagos?offset=0&limit=20` | 200 con items, total, offset y limit |
| GET `/pagos/{id}` | 200 o 404 |
| PATCH `/pagos/{id}` | 200; solo campos enviados, sin id ni valores nulos |
| DELETE `/pagos/{id}` | 204 sin cuerpo |

Al crear se requieren valor y periodo. El valor debe ser mayor que 0.
La fecha se asigna automáticamente con la fecha y hora actual.
Los textos no pueden estar vacíos.

PATCH aplica solo los campos enviados, rechaza valores nulos y campos desconocidos.
Un pago inexistente devuelve 404.

### Modelo Pago

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| id | BIGINT | PRIMARY KEY, IDENTITY |
| valor | NUMERIC(10,2) | NOT NULL, > 0 |
| fecha | DATETIME (timezone) | NOT NULL, valor por defecto: now() |
| periodo | TEXT | NOT NULL, no vacío |

## CRUD de vehículos

La implementación se divide en `app/schemas/vehiculo.py` (validación y respuestas),
`app/routers/vehiculos.py` (APIRouter) y `app/services/vehiculo.py` (operaciones y
transacciones). Reutiliza el modelo `Vehiculo`, `get_session()` y las tablas existentes.

| Método y ruta | Resultado |
| --- | --- |
| `POST /vehiculos` | 201 y vehículo registrado, incluido su id |
| `GET /vehiculos?offset=0&limit=20` | 200 con `items`, `total`, `offset` y `limit` |
| `GET /vehiculos/{id}` | 200 y vehículo, o 404 |
| `PUT /vehiculos/{id}/mensualidad` | 200 y mensualidad activa, o 404 |
| `PATCH /vehiculos/{id}` | 200 y vehículo actualizado, o 404 |
| `DELETE /vehiculos/{id}` | 204 sin cuerpo, o 404 |

La lista se ordena por id ascendente; `offset` empieza en 0 y `limit` admite de
1 a 100 (20 por defecto). `total` es el número total de vehículos, no solo el de
la página. Los ids deben ser enteros positivos dentro del rango de BIGINT.
Cada elemento incluye `estado_mensualidad`, el estado del registro más reciente
de `mensualidad` asociado mediante `mensualidad.id_vehiculo`. Si no tiene registros,
el campo es `null`. La tabla `mensualidad` debe existir en la base de datos; no
forma parte de las migraciones administradas por este proyecto.

Al crear un vehículo, `estado_mensualidad` permite elegir `activo` o `desactivado`;
el backend crea el vehículo y su fila en `mensualidad` en una sola transacción.
PATCH acepta el mismo campo y actualiza el registro de mensualidad más reciente.
`PUT /vehiculos/{id}/mensualidad` activa la mensualidad del vehículo. Inserta un
registro si todavía no existe, o actualiza el más reciente. La operación es idempotente.

Al crear se requieren placa, color, modelo, marca y tipo. El año debe ser un
entero JSON entre 1 y 9999; no se aceptan cadenas, booleanos ni decimales. Los
textos no pueden estar vacíos. La placa se recorta y se convierte a mayúsculas.
Los tipos admitidos son `MOTO`, `AUTOMOVIL` y `CAMIONETA`.

PATCH aplica solo los campos enviados, rechaza valores nulos y campos desconocidos,
incluido `id`. Un objeto vacío conserva el vehículo. Los errores de validación
devuelven 422, una placa duplicada devuelve 409 y un vehículo inexistente, 404.
La unicidad se comprueba en PostgreSQL, también ante peticiones concurrentes;
las transacciones fallidas se revierten. Una clave foránea que impida borrar
devuelve 409 sin eliminar registros relacionados. No hay borrado en cascada en
el servicio. Los fallos generales de base de datos devuelven 503 sin detalles privados.

### Probar desde /docs

Inicia o reinicia el servidor para cargar las nuevas rutas:

```powershell
Set-Location -LiteralPath 'C:\Users\user\Documents\IU DIGITAL\Clase Ingeniería de Software\AutosColombia\backend'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abre <http://127.0.0.1:8000/docs>, despliega **Vehículos** y usa **Try it out**.
Crea un vehículo con POST, copia el id devuelto y úsalo para GET, PATCH y DELETE.
Repite el POST con la misma placa para comprobar 409; prueba PATCH con
`{"color": null}` para comprobar 422. Después de borrar el registro, GET devuelve
404. Estas acciones desde `/docs` sí guardan cambios en tu base.

### Probar desde /docs

Abre <http://127.0.0.1:8000/docs> y despliega las secciones **Usuarios**, **Novedades** y **Pagos**.
Usa **Try it out** para probar cada endpoint.

#### Ejemplo: Crear un usuario
```json
{
  "nombre": "Juan Pérez",
  "documento": "123456789",
  "telefono": "3001234567",
  "fecha_vencimiento": "2025-12-31"
}
```

#### Ejemplo: Crear una novedad
```json
{
  "descripcion": "Rayón en la puerta lateral"
}
```

#### Ejemplo: Crear un pago
```json
{
  "valor": 150000.00,
  "periodo": "2025-01"
}
```

### Probar desde otra terminal de PowerShell

#### Prueba de usuarios
```powershell
$apiUrl = 'http://127.0.0.1:8000'
$testDoc = 'TEST-' + [guid]::NewGuid().ToString('N').Substring(0, 12).ToUpperInvariant()
$payload = @{
    nombre = 'Juan Pérez'
    documento = $testDoc
    telefono = '3001234567'
    fecha_vencimiento = '2025-12-31'
} | ConvertTo-Json
$usuario = Invoke-RestMethod -Method Post -Uri "$apiUrl/usuarios" -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($payload))
try {
    $usuario
    Invoke-RestMethod -Uri "$apiUrl/usuarios?offset=0&limit=20"
    Invoke-RestMethod -Uri "$apiUrl/usuarios/$($usuario.id)"
    Invoke-RestMethod -Method Patch -Uri "$apiUrl/usuarios/$($usuario.id)" -ContentType 'application/json' -Body '{"nombre":"Carlos García"}'
} finally {
    Invoke-WebRequest -Method Delete -Uri "$apiUrl/usuarios/$($usuario.id)" -UseBasicParsing
}
```

#### Prueba de novedades
```powershell
$apiUrl = 'http://127.0.0.1:8000'
$payload = @{
    descripcion = 'Rayón en la puerta lateral'
} | ConvertTo-Json
$novedad = Invoke-RestMethod -Method Post -Uri "$apiUrl/novedades" -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($payload))
try {
    $novedad
    Invoke-RestMethod -Uri "$apiUrl/novedades?offset=0&limit=20"
    Invoke-RestMethod -Uri "$apiUrl/novedades/$($novedad.id)"
    Invoke-RestMethod -Method Patch -Uri "$apiUrl/novedades/$($novedad.id)" -ContentType 'application/json' -Body '{"descripcion":"Rayón en el parabrisas"}'
} finally {
    Invoke-WebRequest -Method Delete -Uri "$apiUrl/novedades/$($novedad.id)" -UseBasicParsing
}
```

#### Prueba de pagos
```powershell
$apiUrl = 'http://127.0.0.1:8000'
$payload = @{
    valor = 150000.00
    periodo = '2025-01'
} | ConvertTo-Json
$pago = Invoke-RestMethod -Method Post -Uri "$apiUrl/pagos" -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($payload))
try {
    $pago
    Invoke-RestMethod -Uri "$apiUrl/pagos?offset=0&limit=20"
    Invoke-RestMethod -Uri "$apiUrl/pagos/$($pago.id)"
    Invoke-RestMethod -Method Patch -Uri "$apiUrl/pagos/$($pago.id)" -ContentType 'application/json' -Body '{"valor":200000.00}'
} finally {
    Invoke-WebRequest -Method Delete -Uri "$apiUrl/pagos/$($pago.id)" -UseBasicParsing
}
```

### Probar desde otra terminal de PowerShell

Este ejemplo crea una placa de prueba aleatoria y elimina solo el vehículo que
acaba de crear. Mantén el backend en ejecución en la primera terminal.

```powershell
$apiUrl = 'http://127.0.0.1:8000'
$testPlate = 'TEST-' + [guid]::NewGuid().ToString('N').Substring(0, 12).ToUpperInvariant()
$payload = @{
    placa = $testPlate
    color = 'Azul'
    modelo = 2025
    marca = 'Prueba'
    tipo = 'AUTOMOVIL'
} | ConvertTo-Json
$vehicle = Invoke-RestMethod -Method Post -Uri "$apiUrl/vehiculos" -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($payload))
try {
    $vehicle
    Invoke-RestMethod -Uri "$apiUrl/vehiculos?offset=0&limit=20"
    Invoke-RestMethod -Uri "$apiUrl/vehiculos/$($vehicle.id)"
    Invoke-RestMethod -Method Patch -Uri "$apiUrl/vehiculos/$($vehicle.id)" -ContentType 'application/json' -Body '{"color":"Rojo"}'
} finally {
    $response = Invoke-WebRequest -Method Delete -Uri "$apiUrl/vehiculos/$($vehicle.id)" -UseBasicParsing
    $response.StatusCode # 204
}
```

### Pruebas automatizadas

Las pruebas habituales no requieren PostgreSQL; la integración se omite por defecto:

```powershell
Set-Location -LiteralPath 'C:\Users\user\Documents\IU DIGITAL\Clase Ingeniería de Software\AutosColombia\backend'
.\.venv\Scripts\python.exe -m pytest -q
```

Para comprobar el CRUD real, usando la base `autos_colombia_db` de `.env` y las
migraciones más recientes:

```powershell
$env:RUN_POSTGRES_TESTS = '1'
try {
    .\.venv\Scripts\python.exe -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Fallaron las pruebas.' }
} finally {
    Remove-Item Env:RUN_POSTGRES_TESTS -ErrorAction SilentlyContinue
}
```

No necesita un servidor HTTP iniciado: TestClient llama a la aplicación y esta
usa PostgreSQL real. Los registros se ejecutan dentro de una transacción exterior
con savepoints que se revierte al terminar, incluso si falla una prueba. No se
crean tablas ni se modifica el esquema; las secuencias de ids pueden avanzar
porque PostgreSQL no revierte sus valores. No se borran registros existentes.
La prueba de conflicto por relación es simulada, ya que el esquema actual no
tiene claves foráneas hacia vehículos; no se añaden relaciones para probarla.

## Implementaciones adicionales

### Autenticación y control de acceso por roles

El sistema implementa autenticación basada en tokens y control de acceso por roles
para usuarios.

#### Endpoint de login

```powershell
POST /usuarios/login
```

Cuerpo de la petición:
```json
{
  "documento": "1040034902",
  "telefono": "3046509495"
}
```

Respuesta:
```json
{
  "usuario": { ... },
  "token": "MzpBRE1JTklTVFJBRE9SOjEwNDAwMzQ5MDI=",
  "rol": "ADMINISTRADOR",
  "permisos": ["gestionar_usuarios", "gestionar_turnos", ...]
}
```

#### Uso del token

Para todas las operaciones de la API, el token debe enviarse en el header:
```
Authorization: Bearer <token>
```

#### Permisos por rol

| Permiso | ADMINISTRADOR | EMPLEADO |
| --- | --- | --- |
| gestionar_usuarios | ✅ | ❌ |
| gestionar_turnos | ✅ | ✅ |
| registrar_ausentismos | ✅ | ✅ |
| cambiar_roles | ✅ | ❌ |
| editar_celdas | ✅ | ❌ |
| eliminar_celdas | ✅ | ❌ |
| editar_empleados | ✅ | ❌ |
| gestionar_operadores | ✅ | ❌ |

#### Restriciones en endpoints

- **POST /usuarios**: Deshabilitado (nadie puede crear usuarios por API)
- **PATCH /usuarios/{id}**: Deshabilitado (nadie puede modificar usuarios por API)
- **DELETE /usuarios/{id}**: Deshabilitado (nadie puede eliminar usuarios por API)
- **GET /usuarios**: Solo administradores pueden ver la lista de usuarios
- **GET /cobertura-semanal**: Público (no requiere autenticación)

**Nota**: Los usuarios se crean directamente en la base de datos o por otros medios, no por la API pública.

**Actualización de permisos**: Ahora ni administradores ni empleados pueden gestionar usuarios (crear/editar/eliminar) por la API. Solo los administradores pueden ver la lista de usuarios.

### Crear usuarios directamente en PostgreSQL

Dado que la gestión de usuarios está deshabilitada en la API, los usuarios se crean directamente en la base de datos:

```sql
INSERT INTO usuario (nombre, documento, telefono, fecha_vencimiento, rol, turno, horas_semana, ausentismo_horas)
VALUES (
    'Nombre del Empleado',
    '123456789',
    '3105555555',
    '2026-12-31',
    'EMPLEADO',
    'MAÑANA',
    42,
    0
);
```

Campos requeridos:
- `nombre`: TEXT, no vacío
- `documento`: TEXT, no vacío, único (se convierte a mayúsculas)
- `telefono`: TEXT, no vacío
- `fecha_vencimiento`: DATE, >= 1900-01-01
- `rol`: 'ADMINISTRADOR' o 'EMPLEADO'
- `turno`: 'MAÑANA', 'TARDE', 'NOCHE' o 'RESPALDO'
- `horas_semana`: INT, entre 1 y 84
- `ausentismo_horas`: INT, entre 0 y 84

### Script para crear múltiples usuarios

Puedes usar un script Python con psycopg3 para crear usuarios en lote:

```python
import psycopg

empleados = [
    ("Nombre 1", "123456789", "3105555555"),
    ("Nombre 2", "987654321", "3205555555"),
]

conn = psycopg.connect(
    host="127.0.0.1",
    port="5432",
    dbname="autos_colombia_db",
    user="postgres",
    password="123456"
)
cursor = conn.cursor()

for nombre, documento, telefono in empleados:
    cursor.execute("""
        INSERT INTO usuario (nombre, documento, telefono, fecha_vencimiento, rol, turno, horas_semana, ausentismo_horas)
        VALUES (%s, %s, %s, '2026-12-31', 'EMPLEADO', 'MAÑANA', 42, 0)
    """, (nombre, documento, telefono))

conn.commit()
conn.close()
```

#### Usuario administrador por defecto

Al iniciar la aplicación, se crea automáticamente un usuario administrador:
- Documento: `ADMIN-001`
- Teléfono: `3001112222`
- Rol: `ADMINISTRADOR`

### Tipos de vehículo extendidos

Además de los tipos originales, el sistema ahora admite:
- `MOTO`
- `AUTOMOVIL`
- `CAMIONETA`
- `FURGON` (agregado)
- `CAMION` (agregado)
- `OTROS` (agregado)

Migración: `4be64630245c`

### Relación Vehículo-Celda

Los vehículos ahora pueden tener una celda asignada directamente mediante el campo
`celda_id` (opcional, nullable). Esto permite asignar vehículos a celdas específicas
sin crear una estancia de entrada/salida.

Migración: `8ec44c2d86d8`

### Campos adicionales en Usuario

El modelo Usuario incluye campos para gestión de empleados:
- `rol`: ADMINISTRADOR o EMPLEADO
- `turno`: MAÑANA, TARDE, NOCHE o RESPALDO
- `horas_semana`: Horas programadas por semana (1-84)
- `ausentismo_horas`: Horas de ausentismo acumuladas (0-84)

El modelo incluye un método `horas_disponibles()` que calcula las horas disponibles
restando las horas de ausentismo a las horas programadas.

### Cobertura semanal

Endpoint público que calcula la cobertura de horas de los empleados:
```powershell
GET /usuarios/cobertura-semanal
```

Devuelve:
- `total_requerido`: 168 horas (requerido para cubrir 24/7)
- `total_programado`: Suma de horas_semana de todos los empleados
- `total_disponible`: Horas disponibles (programadas - ausentismo)
- `faltante_horas`: Horas faltantes para cubrir 168
- `cobertura_pct`: Porcentaje de cobertura
- `sin_huecos`: Boolean que indica si no hay huecos en la operación

### Historial de migraciones

| Revisión | Descripción |
| --- | --- |
| 0001 | Crea vehiculo, celda y operador |
| 0002 | Crea estancia |
| 68a8a3380d1d | Crea usuario, novedad y pago |
| 8ec44c2d86d8 | Agrega celda_id a vehiculo |
| 4be64630245c | Agrega tipos FURGON, CAMION, OTROS a vehiculo |

Versión actual: `4be64630245c (head)`

## Migración 68a8a3380d1d - Usuario, Novedad y Pago

La migración `68a8a3380d1d` agrega tres nuevas tablas al esquema:

### Tablas creadas

1. **usuario** - Gestión de usuarios del sistema
   - id (BIGINT, PRIMARY KEY, IDENTITY)
   - nombre (TEXT, NOT NULL)
   - documento (TEXT, NOT NULL, UNIQUE)
   - telefono (TEXT, NOT NULL)
   - fecha_vencimiento (DATE, NOT NULL)

2. **novedad** - Registro de novedades/incidentes
   - id (BIGINT, PRIMARY KEY, IDENTITY)
   - descripcion (TEXT, NOT NULL)
   - fecha (DATETIME with timezone, NOT NULL, default: now())

3. **pago** - Registro de pagos
   - id (BIGINT, PRIMARY KEY, IDENTITY)
   - valor (NUMERIC(10,2), NOT NULL)
   - fecha (DATETIME with timezone, NOT NULL, default: now())
   - periodo (TEXT, NOT NULL)

### Archivos creados

- `app/models.py` - Modelos Usuario, Novedad, Pago
- `app/schemas/usuario.py` - Schemas de validación para usuarios
- `app/schemas/novedad.py` - Schemas de validación para novedades
- `app/schemas/pago.py` - Schemas de validación para pagos
- `app/services/usuario.py` - Lógica de negocio para usuarios
- `app/services/novedad.py` - Lógica de negocio para novedades
- `app/services/pago.py` - Lógica de negocio para pagos
- `app/routers/usuarios.py` - Endpoints de API para usuarios
- `app/routers/novedades.py` - Endpoints de API para novedades
- `app/routers/pagos.py` - Endpoints de API para pagos
- `migrations/versions/68a8a3380d1d_agregar_usuario_novedad_pago.py` - Migración

### Aplicar la migración

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini upgrade head
```

### Verificar migración aplicada

```powershell
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini current
# Debe mostrar: 68a8a3380d1d (head)
```
