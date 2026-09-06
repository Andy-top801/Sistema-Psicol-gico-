2. Proceso/patrón de desarrollo por Historia de Usuario 

| Rol | Integrante(s) |
|---|---|
| PRODUCT OWNER | Condori Diaz Marilyn Esther |
| SCRUM MASTER | Delgado Rojas Alberto Caleb |
| DEVELOPMENT TEAM | Mujica Vallejos Andy Mauricio; Velasco Soliz Rolando; Larrazabal Rojas Julio Cesar; Romero Saavedra Maria Ilse |


2.1 Diseño 
2.1.1 Diseño de la arquitectura 

El siguiente diagrama de despliegue ilustra la distribución de la arquitectura e infraestructura del sistema SIGEPSI:

```plantuml
@startuml Diagrama_Despliegue_Sprint0

node "INTERNET" as Internet {
  component "Proveedor de\nServicios" as ISP
}

node "ROUTE\n<<device>>" as Route

node "SERVIDOR WEB" as WebServer {
  component "<<servidor en la nube>>\nRender" as Render
  component "<<Codigo>>\nSistema SIGEPSI\n(SaaS Multi-Tenant)" as System
}

node "SERVIDOR BASE DE DATOS" as DBServer {
  component "<<gestor de base de datos>>\nPostgreSQL" as Postgres
}

node "USUARIO" as User {
  component "Navegador\nWeb (Angular)" as NavWeb
  component "Navegador\nMóvil (Flutter)" as NavMovil
}

Internet -down- WebServer
note on link: HTTPS

Route -right- WebServer
note on link: HTTPS

User -up- WebServer
note on link: HTTPS

WebServer -right- DBServer
note on link: TCP/IP
@enduml
```

2.1.2 Diseño de datos 
A continuación se presenta el script SQL de la base de datos para el Sprint 0, contemplando el esquema `public` para los datos compartidos (Multi-Tenant) y un esquema específico para los datos aislados de un centro:

```sql
-- ESQUEMA PUBLIC (Datos Compartidos de la Plataforma)
CREATE SCHEMA IF NOT EXISTS public;

-- Tabla para gestionar los centros psicológicos suscritos
CREATE TABLE public.tenants_tenant (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    schema_name VARCHAR(63) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dominios asociados a cada tenant
CREATE TABLE public.tenants_dominio (
    id SERIAL PRIMARY KEY,
    dominio VARCHAR(253) UNIQUE NOT NULL,
    tenant_id INTEGER REFERENCES public.tenants_tenant(id) ON DELETE CASCADE,
    es_primario BOOLEAN DEFAULT FALSE
);

-- Cuenta del SuperAdministrador de la plataforma
CREATE TABLE public.accounts_superadmin (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- =========================================================
-- ESQUEMA POR TENANT (Ejemplo para un centro específico 'centro_schema')
-- Este esquema se crea automáticamente al registrar un nuevo centro
CREATE SCHEMA IF NOT EXISTS centro_schema;

-- Roles del sistema dentro del centro
CREATE TABLE centro_schema.accounts_rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- Usuarios registrados del centro
CREATE TABLE centro_schema.accounts_usuario (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    rol_id INTEGER REFERENCES centro_schema.accounts_rol(id) ON DELETE SET NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permisos individuales del sistema dentro del centro
CREATE TABLE centro_schema.accounts_permiso (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- Relación muchos a muchos entre roles y permisos
CREATE TABLE centro_schema.accounts_rol_permiso (
    id SERIAL PRIMARY KEY,
    rol_id INTEGER REFERENCES centro_schema.accounts_rol(id) ON DELETE CASCADE,
    permiso_id INTEGER REFERENCES centro_schema.accounts_permiso(id) ON DELETE CASCADE,
    UNIQUE(rol_id, permiso_id)
);

-- Datos institucionales del centro psicológico
CREATE TABLE centro_schema.core_centro (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(255),
    logo VARCHAR(255),
    horario_atencion TEXT,
    configuracion JSONB
);

-- Tokens temporales para la recuperación de contraseñas
CREATE TABLE centro_schema.accounts_token_recuperacion (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES centro_schema.accounts_usuario(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    fecha_expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE
);
```

2.1.3 Diseño de la lógica de negocio 
Diagramas de comunicación (colaboración) de los Casos de Uso del Sprint 0, incluyendo el CU27, diseñados formalmente con formato de comunicación:

```plantuml
@startuml Comunicacion_CU1_GestionarCentros
title CU1 - Gestionar centros psicológicos (Multi-Tenant)

actor "SuperAdministrador" as Admin
boundary "UI Plataforma" as UI
control "TenantController" as API
entity "Tenant" as Model
database "Base de Datos" as DB

Admin -right-> UI : 1: Ingresa datos del centro
UI -right-> API : 2: POST /api/tenants/
API -down-> Model : 3: Validar unicidad
Model -down-> DB : 4: Consultar esquema\n6: Insertar Tenant
DB .up.> Model : 5: Resultado\n7: Confirmación
Model .up.> API : 8: Tenant creado
API .left.> UI : 9: 201 Created
UI .left.> Admin : 10: Mensaje de éxito
@enduml
```

```plantuml
@startuml Comunicacion_CU2_Autenticacion
title CU2 - Gestionar inicio de sesión y autenticación

actor "Usuario" as User
boundary "Login UI" as UI
control "AuthController" as API
entity "Usuario" as Model
database "Base de Datos" as DB

User -right-> UI : 1: Ingresa credenciales
UI -right-> API : 2: POST /api/auth/login/
API -down-> Model : 3: Buscar usuario\n8: Generar JWT
Model -down-> DB : 4: Query por email
DB .up.> Model : 5: Datos (hash)
Model -> Model : 6: Verificar password\n7: Validar tenant
Model .up.> API : 9: Usuario válido
API .left.> UI : 10: 200 OK (JWT)
UI .left.> User : 11: Redirige al Dashboard
@enduml
```

```plantuml
@startuml Comunicacion_CU3_GestionarUsuarios
title CU3 - Gestionar usuarios

actor "AdministradorCentro" as Admin
boundary "Panel Usuarios UI" as UI
control "UserController" as API
entity "Usuario" as Model
database "Base de Datos" as DB

Admin -right-> UI : 1: Llena formulario de usuario
UI -right-> API : 2: POST /api/users/
API -down-> Model : 3: Validar permisos\n4: Validar datos
Model -down-> DB : 5: Consultar email\n7: Insertar usuario
DB .up.> Model : 6: Resultado\n8: Confirmación
Model .up.> API : 9: Usuario creado
API .left.> UI : 10: 201 Created
UI .left.> Admin : 11: Muestra usuario en lista
@enduml
```

```plantuml
@startuml Comunicacion_CU4_GestionarRoles
title CU4 - Gestionar roles y permisos

actor "AdministradorCentro" as Admin
boundary "Panel Roles UI" as UI
control "RoleController" as API
entity "Rol/Permiso" as Model
database "Base de Datos" as DB

Admin -right-> UI : 1: Selecciona permisos y crea Rol
UI -right-> API : 2: POST /api/roles/
API -down-> Model : 3: Validar admin y datos
Model -down-> DB : 4: Insertar Rol\n6: Insertar Rol_Permiso
DB .up.> Model : 5: Rol ID\n7: Confirmación
Model .up.> API : 8: Rol creado
API .left.> UI : 9: 201 Created
UI .left.> Admin : 10: Mensaje de éxito
@enduml
```

```plantuml
@startuml Comunicacion_CU27_RecuperarContrasena
title CU27 - Recuperar contraseña o credenciales de acceso

actor "Usuario" as User
boundary "Recuperar UI" as UI
control "AuthController" as API
entity "Recuperacion" as Model
database "Base de Datos" as DB
boundary "Servidor Email" as Email

User -right-> UI : 1: Ingresa email registrado
UI -right-> API : 2: POST /api/auth/password-reset/
API -down-> Model : 3: Verificar email
Model -down-> DB : 4: Query usuario\n6: Guardar Token
DB .up.> Model : 5: Encontrado\n7: Confirmación
Model .up.> API : 8: Token generado
API -right-> Email : 9: Enviar enlace
Email .left.> API : 10: Confirmación envío
API .left.> UI : 11: 200 OK
UI .left.> User : 12: Mensaje de confirmación
@enduml
```

2.2 Implementación 
2.2.1. Componentes y artefactos generados 

El siguiente diagrama ilustra los componentes y artefactos principales generados durante el Sprint 0, organizados por capas de sistema de acuerdo al diseño establecido:

```plantuml
@startuml Componentes_Artefactos_Sprint0
skinparam linetype ortho

node "Frontend Web y Móvil (Angular / Flutter)" as Frontend {
    component "<<componente>>\nGestores de Interfaz (UI)" as UI #D6EAF8
    artifact "<<artefacto>>\nlogin.component.ts\ntenant_form.dart" as DartFiles #FADBD8
}

node "Backend: Servidor de Aplicación\n(Django/REST)" as Backend {
    component "<<componente>>\nControladores de Negocio" as Controllers #D5F5E3
    artifact "<<artefacto>>\nviews.py\nmodels.py\nserializers.py" as PyFiles #FCF3CF
}

node "Capa de Datos (PostgreSQL)" as DataLayer {
    artifact "<<artefacto>>\nEsquema_DB.sql\n(Tablas: tenants_tenant, accounts_usuario,\naccounts_rol)" as SchemaDB #E8DAEF
}

Frontend -right-> Backend : HTTPS / JSON
Backend -down-> DataLayer : ORM / SQL
@enduml
```

2.2.1.2. Implementación de la arquitectura del subsistema

El siguiente diagrama de componentes ilustra cómo se interconectan los artefactos generados en la arquitectura del subsistema para el Sprint 0:

```plantuml
@startuml Arquitectura_Subsistema_Sprint0
skinparam linetype ortho
skinparam componentStyle rectangle

node "Subsistema de Autenticación y Centros" as Subsistema {
  component "<<Formulario>>\nUI_GestionTenant.ts" as UI_Pac
  component "<<Formulario>>\nUI_GestionUsuario.ts" as UI_Cita
  component "<<Formulario>>\nUI_RolesPermisos.ts" as UI_Clinica

  component "<<Class>>\nCtrl_Tenant.py" as Ctrl_Pac
  component "<<Class>>\nCtrl_Usuario.py" as Ctrl_Cita
  component "<<Class>>\nCtrl_Rol.py" as Ctrl_Clinica

  component "<<Clase>>\nDjango_SIGEPSI" as Django
  
  UI_Pac --> Ctrl_Pac
  UI_Cita --> Ctrl_Cita
  UI_Clinica --> Ctrl_Clinica
  
  Ctrl_Pac --> Django
  Ctrl_Cita --> Django
  Ctrl_Clinica --> Django
}

component "<<Conexiones>>\nPostgres_Connection" as Connection

Django --> Connection

node "Base de Datos (Multi-tenancy)" as BaseDatos {
  component "<<Gestor>>\nPostgreSQL" as PG
  component "<<table>>\npublic.tenants_tenant" as Tbl_Pac
  component "<<table>>\ntenant.accounts_usuario" as Tbl_Clinica
  component "<<table>>\ntenant.accounts_rol" as Tbl_Cita
  
  PG ..> Tbl_Pac
  PG ..> Tbl_Clinica
  PG ..> Tbl_Cita
}

node "Autenticación y Middlewares" as InfoAuditoria {
  component "<<middleware>>\nTenantMiddleware.py\nAuthMiddleware.py" as Reports
  component "<<views>>\nAuthController.py" as Views
  
  Views ..> Reports
}

Connection --> BaseDatos
Connection --> InfoAuditoria
@enduml
```

2.3 Pruebas 
2.3.1. Plan de pruebas (criterios de aceptación) 

Para el Sprint 0, el plan de pruebas se enfoca en validar la correcta creación del entorno Multi-Tenant, la seguridad en los accesos y la gestión básica de usuarios y roles. A continuación, se detallan los criterios de aceptación para los Casos de Uso desarrollados (CU1, CU2, CU3, CU4 y CU27):

| ID Prueba | Caso de Uso | Descripción de la Prueba | Criterios de Aceptación | Resultado Esperado |
|---|---|---|---|---|
| **PR-01** | CU1 - Gestionar centros | Registro de un nuevo centro psicológico (Tenant) | - Datos obligatorios completos.<br>- El slug de URL debe ser único en la plataforma. | El sistema crea un nuevo esquema aislado en PostgreSQL y retorna un HTTP 201. |
| **PR-02** | CU2 - Autenticación | Inicio de sesión de un usuario registrado | - Email y contraseña correctos.<br>- El usuario debe pertenecer al tenant especificado. | El sistema valida las credenciales y devuelve un token JWT válido (HTTP 200). |
| **PR-03** | CU3 - Gestionar usuarios | Creación de un usuario interno para el centro | - Petición autorizada con JWT de Administrador.<br>- Email no debe existir en el mismo tenant.<br>- La contraseña debe cumplir con los requisitos de seguridad (mínimo 8 caracteres, al menos una mayúscula, una minúscula, un número y un carácter especial), notificando al usuario exactamente qué parámetro no cumple si la validación falla. | Usuario insertado exitosamente en el esquema del centro (HTTP 201). En caso de no cumplir requisitos de contraseña, el frontend o la API informará específicamente el parámetro no cumplido. |
| **PR-04** | CU4 - Gestionar roles | Creación de rol y asignación de permisos | - Nombre del rol único.<br>- Seleccionar al menos un permiso de la lista. | Se registra el rol y se crean las relaciones en `accounts_rol_permiso` (HTTP 201). |
| **PR-05** | CU27 - Recuperar contraseña | Solicitud de recuperación mediante email y restablecimiento | - El email ingresado debe existir en la base de datos del tenant.<br>- La nueva contraseña ingresada debe ser segura (8+ caracteres, mayúscula, minúscula, número y carácter especial), mostrando dinámicamente qué parámetro no se cumple si la validación falla. | Se genera un token de seguridad temporal y se simula el envío del correo electrónico con el enlace (HTTP 200). Al confirmar el restablecimiento, se valida la contraseña detalladamente. |

2.3.2 Reporte de prueba

El reporte de pruebas evidencia los resultados de la ejecución de los casos definidos en el entorno de desarrollo para validar la correcta integración del backend (Django) y frontend (Angular/Flutter).

| ID Prueba | Fecha de Ejecución | Entorno de Prueba | Estado | Observaciones / Notas Técnicas |
|---|---|---|---|---|
| **PR-01** | 22/08/2026 | Desarrollo (Postman / Local) | ✅ Exitoso | El middleware enruta correctamente las peticiones al nuevo esquema de la base de datos. |
| **PR-02** | 22/08/2026 | Desarrollo (Angular / Local) | ✅ Exitoso | El JWT se genera correctamente incluyendo el `tenant_id` y `rol_id` en el Payload. |
| **PR-03** | 22/08/2026 | Desarrollo (Angular / Local) | ✅ Exitoso | Las validaciones de aislamiento funcionan. Adicionalmente, el formulario web muestra dinámicamente en tiempo real qué parámetros específicos de seguridad (mayúsculas, minúsculas, números o caracteres especiales) faltan por cumplir en la contraseña. |
| **PR-04** | 22/08/2026 | Desarrollo (Angular / Local) | ✅ Exitoso | Las relaciones de permisos se mapean correctamente y el frontend recibe la lista estructurada. |
| **PR-05** | 22/08/2026 | Desarrollo (Postman / Local / Flutter) | ✅ Exitoso | El token se guarda en la tabla `accounts_token_recuperacion` con estado `usado = FALSE`. Al restablecer la contraseña desde la app móvil, el validador analiza secuencialmente los requisitos y devuelve un mensaje detallado informando exactamente cuál de los parámetros de seguridad no se cumple. |