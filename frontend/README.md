## autores

### Oscar Rene Peñaloza Ardila
### Andres Mauricio Quintero Rios

### Docente

### Reinaldo Rojas Lopez

# Autos Colombia Frontend

Aplicación web desarrollada en Angular 22 para la gestión operativa de un centro de control vehicular. El sistema está orientado a facilitar la administración del ingreso y salida de vehículos, así como la gestión de usuarios, operaciones, celdas, pagos y novedades del negocio.

## Descripción general

La interfaz permite gestionar de forma centralizada los principales procesos del sistema. Está diseñada para dos tipos de usuarios: un administrador, que maneja la parte operativa y administrativa, y un usuario común, que puede acceder al módulo de control de acceso.

El proyecto usa componentes standalone, formularios reactivos, navegación por rutas y protección de acceso según el rol autenticado. Además, contempla una capa de integración con el backend mediante proxy local para consumir los servicios del sistema.

## Funcionalidades implementadas

Hasta el momento, la aplicación incluye las siguientes funciones:

- Inicio de sesión con selección de rol.
- Validación de acceso según el perfil autenticado.
- Control de acceso para registrar entrada y salida de vehículos.
- Gestión de usuarios.
- Gestión de operadores.
- Gestión de vehículos.
- Gestión de celdas.
- Gestión de pagos.
- Gestión de novedades.
- Visualización del listado y estado de cada módulo.
- Navegación por secciones principales de la aplicación.
- Protección de rutas para restringir accesos no autorizados.
- Cierre de sesión desde la interfaz.

## Roles del sistema

### Administrador
El administrador tiene acceso a los módulos de administración y gestión del sistema. Su flujo principal permite operar sobre:

- Usuarios
- Operadores
- Vehículos
- Celdas
- Pagos
- Novedades

### Usuario
El usuario tiene acceso a la funcionalidad operativa básica del sistema, principalmente:

- Control de acceso

La pantalla de control de acceso está restringida para usuarios no administrativos, con el objetivo de evitar que el administrador intervenga directamente en la operación diaria de entrada y salida de vehículos.

## Módulos principales

### 1. Login
Pantalla de autenticación donde se selecciona el rol y se ingresa la información del usuario para iniciar sesión.

### 2. Control de acceso
Módulo operativo para registrar la entrada y salida de vehículos. Es la pantalla principal del flujo de operación del usuario.

### 3. Gestión de vehículos
Permite consultar y administrar la información del parque automotor del sistema.

### 4. Gestión de usuarios
Permite administrar los usuarios del sistema y sus permisos.

### 5. Gestión de operadores
Permite administrar la información de los operadores relacionados con la operación del centro.

### 6. Gestión de celdas
Módulo para manejar las celdas o espacios disponibles del sistema.

### 7. Gestión de novedades
Permite registrar, editar y eliminar novedades o avisos importantes dentro del sistema.

### 8. Gestión de pagos
Módulo para gestionar pagos o información asociada a transacciones del negocio.

## Rutas principales

La aplicación cuenta con las siguientes rutas:

- `/` - Inicio
- `/login` - Inicio de sesión
- `/control-acceso` - Registro de acceso vehicular
- `/gestion/vehiculos` - Administración de vehículos
- `/gestion/usuarios` - Administración de usuarios
- `/gestion/operadores` - Administración de operadores
- `/gestion/celdas` - Administración de celdas
- `/gestion/novedades` - Administración de novedades
- `/gestion/pagos` - Administración de pagos

La página Inicio permite consultar el historial de estancias con filtros por rango
de fechas de entrada y placa parcial. Los resultados se ordenan del más reciente al
más antiguo y se paginan en bloques de 10.

También muestra las estancias abiertas con los datos registrados de cada vehículo,
su celda y el operador de entrada; la consulta es independiente del flujo operativo.

En Inicio los usuarios con sesión pueden registrar novedades vinculadas a una placa.
El sistema guarda la fecha y hora del momento de registro. El historial de novedades,
filtrable por fecha y placa, solo se presenta a administradores.

## Usuarios registrados y acceso

La aplicación cuenta con los siguientes usuarios visibles en el sistema:

### Administradores
- Oscar Rene Peñaloza Ardila
  - Documento: `4387888`
  - Teléfono: `3173746252`
- Andres Mauricio Quintero Rios
  - Documento: `1040034902`
  - Teléfono: `3046509495`

### Empleados
- Liliana Yaneht Carmona Montoya
  - Documento: `1040038823`
  - Teléfono: `3124755000`
- Thiago Alejandro Rios Lopez
  - Documento: `1040052403`
  - Teléfono: `3046508800`
- Jesús Antonio Arcila Rios
  - Documento: `1040034454`
  - Teléfono: `3124758600`

> En la pantalla de login se selecciona el rol y se ingresa la información del usuario para acceder según el perfil.

## Requisitos del proyecto

- Node.js
- npm
- Backend funcional para consumir la API
- Navegador moderno

## Instalación y ejecución

En Windows puedes arrancar la aplicación con estos comandos:

```powershell
Set-Location -LiteralPath 'D:\IU Digital\ingenieria de software\AutosColombia-main\frontend'
npm install
npm start -- --host 127.0.0.1 --port 4200
```

Luego abre la siguiente URL:

```text
http://127.0.0.1:4200
```

## Conexión con el backend

El frontend se conecta con el backend a través de un proxy configurado en `proxy.conf.json`.

Entre las rutas principales se encuentran:

- `/health`
- `/vehiculos`
- `/vehiculos/**`
- Endpoints de servicios para usuarios, operadores, accesos y administración

Esto permite que la aplicación haga peticiones al backend local, evitando conflictos con los origenes cruzados durante el desarrollo.

## Verificación y pruebas

Para compilar la aplicación:

```powershell
npm run build
```

Para ejecutar la suite de pruebas:

```powershell
npm test -- --watch=false
```

## Estado actual del proyecto

El proyecto frontend se encuentra en una etapa funcional de gestión operativa y administrativa. Ya permite la autenticación por roles, gestión de módulos principales y acceso diferenciado según el tipo de usuario.

Este README refleja el alcance actual del sistema y las funcionalidades disponibles hasta este punto del proyecto.
