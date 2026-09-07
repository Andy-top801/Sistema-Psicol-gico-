# 📘 Guía de Compilación, Ejecución y Pruebas — SIGEPSI Prototipo (Sprint 0 y Sprint 1)

> **Proyecto:** SIGEPSI — Sistema de Gestión para Centros Psicológicos  
> **Arquitectura:** Backend (Django REST + Multi-Tenant PostgreSQL) · Web (Angular 17) · Móvil (Flutter)  
> **Base de Datos:** PostgreSQL (requerido para multi-tenancy y esquemas independientes)

---

## 📋 Tabla de Contenido

1. [Prerrequisitos Globales](#1-prerrequisitos-globales)
2. [Jerarquía de Roles y Arquitectura de Usuarios](#2-jerarquía-de-roles-y-arquitectura-de-usuarios)
3. [Backend (Django REST Framework)](#3-backend-django-rest-framework)
4. [Web (Angular 17)](#4-web-angular-17)
5. [Móvil (Flutter)](#5-móvil-flutter)
6. [Ejecución Integrada (Full Stack)](#6-ejecución-integrada-full-stack)
7. [Credenciales de Prueba](#7-credenciales-de-prueba)
8. [Endpoints de la API](#8-endpoints-de-la-api)
9. [Solución de Problemas Comunes](#9-solución-de-problemas-comunes)

---

## 1. Prerrequisitos Globales

Asegurarse de tener instalado:

| Herramienta        | Versión Mínima | Verificar con            | Propósito / Notas |
|--------------------|----------------|--------------------------|-------------------|
| Python             | 3.10+ (3.13)   | `python --version`       | Backend Django REST y scripts |
| PostgreSQL         | 14+ (18)       | `psql --version`         | Multi-Tenancy con esquemas independientes |
| Node.js            | 18+ (22+)      | `node --version`         | Frontend Web Angular 17 |
| npm                | 9+             | `npm --version`          | Gestor de paquetes de Node |
| Angular CLI        | 17+            | `ng version`             | Framework Web SPA |
| Flutter SDK        | 3.20+ (3.47+)  | `flutter --version`      | Aplicación Móvil multiplataforma |
| Dart SDK           | 3.0+ (3.13+)   | `dart --version`         | Lenguaje de Flutter |
| Java JDK / JBR     | 17+ (JDK 25)   | `java -version`          | Gradle 9.3.1 y compilación de Android (`JAVA_HOME`) |
| Git                | 2.x            | `git --version`          | Control de versiones |

---

## 2. Jerarquía de Roles y Arquitectura de Usuarios

En SIGEPSI, la arquitectura multi-tenant divide la responsabilidad en dos planos bien diferenciados: **Nivel Plataforma Global (SaaS)** y **Nivel Centro Psicológico (Tenant)**.

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                   NIVEL 0: PLATAFORMA GLOBAL (Esquema: public)                    ║
║                                                                                   ║
║  👑 SuperAdmin (beto.caleb.delgado.rojas@gmail.com)                               ║
║     • Dueño/Operador del software SaaS SIGEPSI.                                   ║
║     • Da de alta nuevos centros, gestiona planes y contratos.                    ║
║     • Suspende o reactiva acceso a centros.                                       ║
║     • ⛔ NO tiene acceso a historias clínicas ni datos privados de pacientes.     ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
╔═══════════════════════════════════╗ ╔═══════════════════════════════════╗
║  TENANT 1: "centro_esperanza"     ║ ║  TENANT 2: "mentesana"            ║
║  (Base de Datos / Esquema Propio) ║ ║  (Base de Datos / Esquema Propio) ║
╠═══════════════════════════════════╣ ╠═══════════════════════════════════╣
║                                   ║ ║                                   ║
║ 🏢 1. ADMIN DEL CENTRO (Director) ║ ║ 🏢 1. ADMIN DEL CENTRO (Director) ║
║    • Máxima autoridad del centro. ║ ║    • Máxima autoridad del centro. ║
║    • Configura datos, horarios.   ║ ║    • Configura datos, horarios.   ║
║    • Gestiona usuarios y roles.   ║ ║    • Gestiona usuarios y roles.   ║
║                                   ║ ║                                   ║
║ 📋 2. COORDINADOR CLÍNICO         ║ ║ 📋 2. COORDINADOR CLÍNICO         ║
║    • Supervisión terapéutica.     ║ ║    • Supervisión terapéutica.     ║
║    • Triage y asignación de casos.║ ║    • Triage y asignación de casos.║
║    • Monitoreo de alertas/riesgo. ║ ║    • Monitoreo de alertas/riesgo. ║
║    • (NO es el admin técnico).    ║ ║    • (NO es el admin técnico).    ║
║                                   ║ ║                                   ║
║ 🩺 3. PSICÓLOGO / TERAPEUTA       ║ ║ 🩺 3. PSICÓLOGO / TERAPEUTA       ║
║    • Atiende a sus pacientes.     ║ ║    • Atiende a sus pacientes.     ║
║    • Notas de sesión y tareas.    ║ ║    • Notas de sesión y tareas.    ║
║    • Teleconsultas y agenda.      ║ ║    • Teleconsultas y agenda.      ║
║                                   ║ ║                                   ║
║ 💼 4. RECEPCIONISTA               ║ ║ 💼 4. RECEPCIONISTA               ║
║    • Registro y alta de pacientes.║ ║    • Registro y alta de pacientes.║
║    • Agendar y confirmar citas.   ║ ║    • Agendar y confirmar citas.   ║
║    • ⛔ NO ve notas clínicas.     ║ ║    • ⛔ NO ve notas clínicas.     ║
║                                   ║ ║                                   ║
║ 🧑 5. PACIENTE                    ║ ║ 🧑 5. PACIENTE                    ║
║    • Portal web/móvil propio.     ║ ║    • Portal web/móvil propio.     ║
║    • Ver citas, tareas y sesión.  ║ ║    • Ver citas, tareas y sesión.  ║
╚═══════════════════════════════════╝ ╚═══════════════════════════════════╝
```

### 📌 ¿Quién hace qué? Tabla Comparativa de Permisos

| Rol | Nivel / Esquema | ¿Qué puede hacer? | ¿Qué NO puede hacer? |
|---|---|---|---|
| **SuperAdmin** | Global (`public`) | Crear/suspender centros psicológicos, configurar dominios, gestionar planes SaaS. | Ver expedientes clínicos, agendar citas o modificar datos internos de un centro. |
| **Admin Centro** | Centro (`tenant`) | Administrador general del centro: crear/dar de baja usuarios (psicólogos, recepcionistas), asignar roles, configurar horarios y políticas del centro. | Gestionar otros centros de la plataforma o cambiar configuraciones globales SaaS. |
| **Coordinador Clínico** | Centro (`tenant`) | Supervisión clínica, triage de pacientes entrantes, asignación de pacientes a psicólogos, revisión de historias clínicas y alertas de abandono/riesgo. | **No es el admin del sitio:** No gestiona cuentas técnicas, ni contraseñas del personal, ni políticas del centro. |
| **Psicólogo** | Centro (`tenant`) | Atender citas, escribir notas de evolución, crear tareas terapéuticas inter-sesión, teleconsulta con sus pacientes asignados. | Ver pacientes de otros psicólogos (a menos que sea transferido) o gestionar usuarios. |
| **Recepcionista** | Centro (`tenant`) | Registrar pacientes, agendar citas en calendario general, confirmar asistencias. | Ver notas confidenciales de sesiones psicológicas o diagnósticos reservados. |
| **Paciente** | Centro (`tenant`) | Consultar sus próximas citas, acceder a teleconsulta, responder tareas terapéuticas. | Acceder a datos de otros pacientes o al panel administrativo. |

---

## 3. Backend (Django REST Framework)

### 3.1 Estructura del Backend

```
backend/
├── sigepsi/              # Proyecto Django (settings, urls)
├── accounts/             # App: Usuarios, Roles, Permisos, Auth JWT
├── core/                 # App: Configuración del Centro Psicológico
├── tenants/              # App: Multi-Tenancy (django-tenants)
├── clinica/              # App Sprint 1: Especialidades, Psicólogos, Horarios, Pacientes y Expedientes
├── agenda/               # App Sprint 1: Citas, Bloqueo Concurrente, Teleconsulta Jitsi, KPIs y Alertas
├── tests/                # Tests unitarios (pytest/django-tenants)
├── manage.py
├── requirements.txt
├── verify_sprint0.py     # Verificación integral Sprint 0 (25 pruebas)
├── verify_sprint1.py     # Verificación integral Sprint 1 (24 pruebas)
└── scratch/
    └── verify_all_use_cases.py  # Suite de verificación de todos los Casos de Uso (36 pruebas CU1-CU14, CU27)
```

### 3.2 Configurar PostgreSQL

> ⚠️ **PostgreSQL es obligatorio** — El sistema usa `django-tenants` que requiere esquemas PostgreSQL para multi-tenancy. SQLite **no funciona**.

```sql
-- Conectarse a PostgreSQL (como usuario postgres)
psql -U postgres

-- Crear la base de datos
CREATE DATABASE sigepsi_db;

-- (Opcional) Crear usuario dedicado
CREATE USER sigepsi_user WITH PASSWORD 'sigepsi_password';
ALTER ROLE sigepsi_user SET client_encoding TO 'utf8';
ALTER ROLE sigepsi_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sigepsi_user SET timezone TO 'America/La_Paz';
GRANT ALL PRIVILEGES ON DATABASE sigepsi_db TO sigepsi_user;

-- Salir
\q
```

La configuración por defecto en `settings.py` usa:
- **DB_NAME:** `sigepsi_db`
- **DB_USER:** `postgres`
- **DB_PASSWORD:** `postgres`
- **DB_HOST:** `localhost`
- **DB_PORT:** `5432`

Se pueden modificar mediante variables de entorno:

```powershell
$env:DB_NAME = "sigepsi_db"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "tu_password"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
```

### 3.3 Crear Entorno Virtual y Dependencias

```powershell
# Navegar a la carpeta backend
cd prototipo\backend

# Crear entorno virtual (si no existe)
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

**Dependencias principales:**
| Paquete                       | Propósito                                 |
|-------------------------------|-------------------------------------------|
| `django>=5.0,<6.2`           | Framework web                             |
| `djangorestframework>=3.14`   | API REST                                  |
| `djangorestframework-simplejwt` | Autenticación JWT                       |
| `django-tenants>=3.7`         | Multi-tenancy con esquemas PostgreSQL     |
| `psycopg2-binary>=2.9`        | Driver PostgreSQL                         |
| `django-cors-headers>=4.3`    | CORS para frontend                        |
| `pyjwt`                       | Tokens JWT firmados para salas WebRTC     |

### 3.4 Migraciones y Base de Datos

```powershell
# Migrar esquema public (compartido entre todos los tenants)
python manage.py migrate_schemas --shared

# Migrar esquemas de tenants (incluye apps clinica y agenda)
python manage.py migrate_schemas --tenant
```

> **Nota:** `django-tenants` reemplaza el comando `migrate` estándar con `migrate_schemas`.

### 3.5 Sembrar Datos de Prueba (Sprint 0 y Sprint 1)

```powershell
# 1. Sembrar estructura institucional base (Sprint 0: tenants, roles, usuarios)
python manage.py seed_data

# 2. Sembrar datos clínicos y agenda operativa (Sprint 1: especialidades, psicólogos, pacientes, citas)
python manage.py seed_sprint1
```

Estos comandos crean automáticamente:
- ✅ **Tenant `public`** con dominio `localhost`
- ✅ **SuperAdmin Global:** `beto.caleb.delgado.rojas@gmail.com` / `Admin1234*`
- ✅ **Centro "Esperanza"** (tenant: `centro_esperanza`) y **Centro "MenteSana"** (tenant: `mentesana`)
- ✅ **Roles y Permisos RBAC** completos
- ✅ **5 Especialidades Clínicas** (Cognitivo-Conductual, Clínica, Neuropsicología, etc.)
- ✅ **Psicólogos con perfil y colegiatura:** `carlos.mendoza@centroesperanza.com` / `Psicologo123*`
- ✅ **Franjas horarias semanales de atención** configuradas
- ✅ **Pacientes demo** con expedientes (`EXP-YYYYMM-XXXX`) y tutores legales para menores
- ✅ **Citas médicas con estados:** `PROGRAMADA`, `CONFIRMADA`, `REALIZADA`, `CANCELADA`
- ✅ **Salas WebRTC Jitsi Meet** asociadas y **Alertas Clínicas** tempranas

### 3.6 Ejecutar el Servidor Backend

```powershell
# Iniciar servidor de desarrollo (puerto 8000)
python manage.py runserver
```

El servidor quedará disponible en: **http://localhost:8000**

Verificar que funciona abriendo en el navegador:
- `http://localhost:8000/api/tenants/public/` → Lista de centros públicos

### 3.7 Ejecutar Suites de Pruebas del Backend

#### A. Verificación del Sprint 0 (25 Pruebas: Multi-tenant, Auth y RBAC)

```powershell
python verify_sprint0.py
```
Evalúa 25 casos de prueba de registro, login JWT, aislamiento de esquemas, administración de roles y restablecimiento de contraseña.

#### B. Verificación del Sprint 1 (24 Pruebas: Clínica, Agenda, Teleconsulta, KPIs)

```powershell
python verify_sprint1.py
```
Evalúa 24 casos de prueba de directorio médico, disponibilidad horaria, expedientes de pacientes, bloqueo pesimista concurrente, salas WebRTC Jitsi Meet, cancelación con reglas de anticipación (2h), KPIs de ocupación y alertas clínicas.

#### C. Verificación Exhaustiva de Todos los Casos de Uso (36 Pruebas: CU1 a CU14 + CU27)

```powershell
python scratch\verify_all_use_cases.py
```
Ejecuta de extremo a extremo todas las Historias de Usuario (HU-01 a HU-22) y Casos de Uso del sistema:

| Caso de Uso | Historia de Usuario | Descripción Funcional |
|:---|:---|:---|
| **CU1** | HU-03, HU-04, HU-07, HU-08 | Alta de centro, aislamiento PostgreSQL, configuración y suspensión |
| **CU2** | HU-01, HU-02, HU-09 | Registro autónomo, login JWT auto-tenant y blacklist logout |
| **CU27**| HU-10 | Recuperación de contraseña por token temporal criptográfico |
| **CU3** | HU-05 | Gestión de usuarios, edición parcial sin email, toggle activo |
| **CU4** | HU-06 | Catálogo RBAC institucional y asignación dinámica de permisos |
| **CU6** | HU-11 | Directorio de psicólogos, aranceles, biografía y especialidades |
| **CU8** | HU-12 | Matriz semanal de disponibilidad y rechazo de franjas invertidas |
| **CU7** | HU-13, HU-14 | Expedientes con autogeneración de código, tutor obligatorio para menores y `/me/` |
| **CU11**| HU-15, HU-16 | Slots libres (50 min), reserva con bloqueo pesimista y sala WebRTC automática |
| **CU12**| HU-17 | Cancelación anticipada válida (>2h) y rechazo de cancelación tardía (<2h) |
| **CU13**| HU-18, HU-19 | Acceso WebRTC Jitsi con roles (Moderador vs Invitado) y cierre con duración real |
| **CU9** | HU-20 | Dashboard clínico en tiempo real con ocupación, ausentismo e ingresos |
| **CU10**| HU-21 | Generación de alertas clínicas por inasistencias reiteradas y resolución con notas |
| **CU14**| HU-22 | Matriz de eventos para FullCalendar con filtrado por terapeuta |

---

## 4. Web (Angular 17)

### 4.1 Estructura del Frontend Web

```
web/
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── guards/          # Auth guards (authGuard, superAdminGuard, adminCentroGuard)
│   │   │   ├── interceptors/    # HTTP interceptor (JWT + X-Tenant-ID reactivo)
│   │   │   ├── models/          # Interfaces TypeScript (Usuario, Paciente, Psicólogo, Cita, Alerta, etc.)
│   │   │   └── services/        # AuthService, TenantService, UserService, ClinicaService, AgendaService
│   │   ├── layout/              # MainLayoutComponent (sidebar + contenido + perfil)
│   │   ├── modules/
│   │   │   ├── auth/            # Login, Registro autónomo y Recuperación de contraseña
│   │   │   ├── dashboard/       # Dashboard Clínico con KPIs, ausentismo y alertas tempranas
│   │   │   ├── tenants/         # CRUD de centros (SuperAdmin)
│   │   │   ├── users/           # CRUD de usuarios del centro
│   │   │   ├── roles/           # CRUD de roles y permisos RBAC
│   │   │   ├── centro/          # Configuración institucional
│   │   │   ├── pacientes/       # Sprint 1: Gestión de pacientes, autogeneración de expediente y tutores
│   │   │   ├── psicologos/      # Sprint 1: Directorio profesional, colegiatura, tarifas y disponibilidad semanal
│   │   │   ├── agenda/          # Sprint 1: Calendario interactivo FullCalendar, slots 50 min y reserva pesimista
│   │   │   └── teleconsulta/    # Sprint 1: Sala WebRTC Jitsi Meet con roles diferenciados
│   │   ├── app.component.ts
│   │   ├── app.config.ts
│   │   └── app.routes.ts
│   ├── styles.css               # Estilos globales y temas
│   ├── index.html
│   └── main.ts
├── angular.json
├── package.json
└── tsconfig.json
```

### 4.2 Instalar Dependencias

```powershell
# Navegar a la carpeta web
cd prototipo\web

# Instalar dependencias de Node.js
npm install
```

**Tecnologías principales:**
- Angular 17.3 (Standalone Components, Signals, Reactive Forms)
- TypeScript 5.4
- RxJS 7.8
- FullCalendar (@fullcalendar/angular, daygrid, timegrid, interaction)
- Jitsi Meet External API (WebRTC Teleconsulta)

### 4.3 Compilar y Ejecutar en Desarrollo

```powershell
# Iniciar servidor de desarrollo Angular
npm start
# o equivalentemente:
npx ng serve
```

La aplicación quedará disponible en: **http://localhost:4200**

> **Importante:** El backend debe estar corriendo en `http://localhost:8000` para que el frontend pueda comunicarse con la API.

### 4.4 Compilar para Producción

```powershell
# Build de producción
npm run build
```

Los archivos compilados se generan en: `dist/sigepsi-web/`

### 4.5 Compilar en Modo Watch

```powershell
# Recompila automáticamente al detectar cambios
npm run watch
```

### 4.6 Módulos y Rutas Web Disponibles

| Ruta                      | Módulo                     | Funcionalidad / Descripción                      | Roles Autorizados |
|---------------------------|----------------------------|--------------------------------------------------|-------------------|
| `/login`                  | Autenticación              | Login con selección o detección de centro        | Público |
| `/dashboard`              | Dashboard Clínico          | KPIs de ocupación, ausentismo y alertas activas  | Todos los autenticados |
| `/tenants`                | Gestión de centros         | Crear, suspender y administrar centros           | SuperAdmin |
| `/users`                  | Gestión de usuarios        | Alta, edición parcial sin email y desactivación  | Admin Centro |
| `/roles`                  | Roles y permisos RBAC      | Configuración matricial de permisos por rol      | Admin Centro |
| `/centro`                 | Perfil Institucional       | Configuración de datos, logo y aranceles         | Admin Centro |
| `/pacientes`              | Pacientes y Expedientes    | Alta con código `EXP-YYYYMM-XXXX`, tutores       | Admin Centro, Recepción, Terapeuta |
| `/psicologos`             | Directorio Profesional     | Psicólogos, especialidades y franjas horarias    | Admin Centro, Coordinador |
| `/agenda`                 | Agenda y Calendario        | FullCalendar interactivo, slots de 50 min        | Todos |
| `/teleconsulta/:citaId`   | Teleconsulta WebRTC        | Sala Jitsi Meet cifrada (Moderador vs Paciente)  | Psicólogo, Paciente |

---

## 5. Móvil (Flutter)

### 5.1 Estructura de la App Móvil

```
movil/
├── lib/
│   ├── core/
│   │   ├── constants/
│   │   │   └── api_constants.dart    # URLs del backend
│   │   └── theme/
│   │       └── app_theme.dart        # Tema visual oscuro
│   ├── models/
│   │   ├── user_model.dart           # Modelo de usuario
│   │   └── tenant_model.dart         # Modelo de tenant/centro
│   ├── screens/
│   │   ├── login_screen.dart         # Pantalla de login con selector de centro
│   │   ├── dashboard_screen.dart     # Dashboard principal
│   │   ├── password_reset_screen.dart # Recuperación de contraseña
│   │   ├── users_screen.dart         # Listado de usuarios
│   │   ├── roles_screen.dart         # Listado de roles
│   │   ├── tenants_screen.dart       # Listado de centros (SuperAdmin)
│   │   └── centro_config_screen.dart # Config. institucional
│   ├── services/
│   │   └── auth_service.dart         # Servicio de autenticación HTTP
│   └── main.dart                     # Punto de entrada
└── pubspec.yaml
```

### 5.2 Prerrequisito Crítico de Java para Android (Gradle 9 / AGP 9)

> ⚠️ **Importante:** Android Gradle Plugin 9.1.0 y Gradle 9.3.1 requieren **Java 17 o superior** (se recomienda la JVM 25 de Android Studio JBR). Si en la máquina existe una versión anterior como Java 8 en el PATH de Windows, Gradle fallará con el error:  
> *`Gradle requires JVM 17 or later to run. Your build is currently configured to use JVM 8.`*

Para configurarlo de forma permanente:
1. Asegurar que `C:\Users\User\.gradle\gradle.properties` tenga la ruta a la JVM de Android Studio:
   ```properties
   org.gradle.java.home=C:/Program Files/Android/Android Studio/jbr
   ```
2. Verificar en `prototipo/movil/android/gradle.properties`:
   ```properties
   org.gradle.java.home=C:/Program Files/Android/Android Studio/jbr
   ```

### 5.3 Instalar Dependencias y Generar Plataforma Nativa

```powershell
# 1. Navegar a la carpeta móvil
cd prototipo\movil

# 2. Verificar entorno Flutter y dispositivos conectados
flutter doctor

# 3. Generar soporte nativo (Android, Web, Windows)
# (Requerido si no existe la carpeta android/ o si sale 'device not supported')
flutter create --platforms=android,web,windows .

# 4. Obtener paquetes y dependencias Dart
flutter pub get
```

**Dependencias principales:**
| Paquete               | Propósito                            |
|-----------------------|--------------------------------------|
| `http: ^1.2.0`        | Cliente HTTP para llamadas a la API  |
| `shared_preferences`  | Almacenamiento local (tokens JWT)    |
| `google_fonts`         | Tipografía personalizada             |
| `intl`                 | Internacionalización y fechas        |

### 5.3 Configuración de Red y Conexión de Dispositivo Físico (USB)

Para ejecutar la aplicación en tu **celular físico (Samsung, Xiaomi, Motorola, etc.)**:

#### Paso 1: Activar Depuración por USB en el Celular
1. En tu teléfono, ir a **Ajustes > Acerca del teléfono**.
2. Tocar 7 veces consecutivas sobre **Número de compilación** para activar el menú de desarrollador.
3. Ir a **Ajustes > Opciones de desarrollador** y encender **Depuración por USB**.
4. Conectar el celular a la PC mediante cable USB y pulsar **Permitir siempre** en el mensaje emergente que aparece en la pantalla del celular.

#### Paso 2: Redirigir el puerto del Backend (Reverse Port Forwarding)
Para que las peticiones a `http://localhost:8000/api` que haga el celular viajen directamente por el cable USB hasta tu servidor Django en la PC (sin configurar IPs manuales ni depender del Wi-Fi):

```powershell
# Ejecutar adb reverse (usando la ruta del SDK de Android en Windows):
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000

# O directamente si adb está en tus Variables de Entorno PATH:
adb reverse tcp:8000 tcp:8000
```
> Si la consola responde `8000`, el puente está activo exitosamente.

#### Paso 3: Configurar URL del Backend en la App
Verificar que en `lib/core/constants/api_constants.dart` la URL base esté apuntando a:

```dart
class ApiConstants {
  // Con 'adb reverse' por cable USB o en Web, se usa localhost:8000:
  static const String baseUrl = 'http://localhost:8000/api';
  static const String webBaseUrl = 'http://localhost:8000/api';

  // Si se usa emulador de Android Studio (sin USB), usar:
  // static const String baseUrl = 'http://10.0.2.2:8000/api';

  // Si se conecta por Wi-Fi sin cable en la misma red local, usar la IP de tu PC:
  // static const String baseUrl = 'http://192.168.1.XX:8000/api';
  ...
}
```

#### Paso 4: Permisos de Red en `android/app/src/main/AndroidManifest.xml`
Asegurarse de que el manifiesto permita salida a Internet y tráfico HTTP no cifrado hacia el servidor local:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Permiso para realizar peticiones HTTP a la API -->
    <uses-permission android:name="android.permission.INTERNET" />
    <application
        ...
        android:usesCleartextTraffic="true">
```

---

### 5.4 Ejecutar en el Dispositivo Físico o Emulador

```powershell
# 1. Verificar que Flutter reconozca el celular
flutter devices

# Ejemplo de salida:
# SM A566E (mobile) • R5CY620NJLA • android-arm64 • Android 16 (API 36)

# 2. Ejecutar la aplicación en tu celular indicando su identificador:
flutter run -d R5CY620NJLA

# O simplemente ejecutar y seleccionar el número correspondiente a tu teléfono en la lista:
flutter run

# Opciones alternativas:
flutter run -d chrome            # Ejecutar en navegador (Flutter Web)
flutter run -d windows           # Ejecutar como app de escritorio Windows
flutter run --release            # Ejecutar en modo release optimizado
```

> **Consejo durante la ejecución:** Mientras la app corre en tu teléfono, puedes presionar `r` en la consola para **Hot Reload** (recargar cambios instantáneamente) o `R` para **Hot Restart**. Para detenerla presiona `q`.

### 5.5 Compilar APK (Android)

```powershell
# APK de debug
flutter build apk --debug

# APK de producción (release)
flutter build apk --release

# Bundle de producción (AAB para Google Play)
flutter build appbundle --release
```

Los archivos generados se encuentran en:
- APK: `build/app/outputs/flutter-apk/app-release.apk`
- AAB: `build/app/outputs/bundle/release/app-release.aab`

### 5.6 Ejecutar Tests de Flutter

```powershell
# Ejecutar todos los tests unitarios
flutter test

# Ejecutar un test específico
flutter test test/widget_test.dart
```

### 5.7 Probar la App Manualmente

1. Al abrir la app aparece la pantalla de **Login**
2. Seleccionar un centro de la lista (se obtienen del endpoint `/api/tenants/public/`)
3. Ingresar credenciales
4. Navegar por las pantallas del dashboard según el rol

> **Nota:** Para que la app móvil funcione, el backend debe estar corriendo y ser accesible desde el dispositivo/emulador.

---

## 6. Ejecución Integrada (Full Stack)

Para tener todo el sistema funcionando simultáneamente, abrir **3 terminales**:

### Terminal 1 — Backend

```powershell
cd prototipo\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
# → http://localhost:8000
```

### Terminal 2 — Web

```powershell
cd prototipo\web
npm start
# → http://localhost:4200
```

### Terminal 3 — Móvil (Celular físico o Emulador)

```powershell
cd prototipo\movil

# Si usas celular físico conectado por cable USB (Samsung, Xiaomi, etc.):
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000

# Iniciar la app en tu celular:
flutter run
# (O indicar tu dispositivo directamente: flutter run -d <ID_DISPOSITIVO>)
# → Se instalará y abrirá automáticamente en tu celular
```

### Diagrama de Comunicación

```
┌──────────────────────┐         ┌──────────────────────┐
│   Angular Web        │         │   Flutter Móvil      │
│  localhost:4200      │         │   (Emulador/Device)  │
└─────────┬────────────┘         └─────────┬────────────┘
          │ HTTP + JWT + X-Tenant-ID        │ HTTP + JWT + X-Tenant-ID
          │                                 │
          └────────────┬────────────────────┘
                       │
              ┌────────▼────────┐
              │  Django Backend │
              │  localhost:8000 │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  PostgreSQL     │
              │  sigepsi_db     │
              │                 │
              │  ┌──────────┐   │
              │  │ public   │   │ ← SuperAdmin, Tenants
              │  ├──────────┤   │
              │  │esperanza │   │ ← Centro Esperanza
              │  ├──────────┤   │
              │  │mentesana │   │ ← Gabinete MenteSana
              │  └──────────┘   │
              └─────────────────┘
```

---

## 7. Credenciales de Prueba

### SuperAdmin (Esquema Public)

| Email                                  | Contraseña   | Rol        | Ámbito |
|----------------------------------------|-------------|------------|--------|
| beto.caleb.delgado.rojas@gmail.com     | Admin1234*  | SuperAdmin | Plataforma Global (SaaS) |
| admin@sigepsi.com (alias secundario)   | Admin1234*  | SuperAdmin | Plataforma Global (SaaS) |

### Centro Psicológico Esperanza (`centro_esperanza`)

| Email                                | Contraseña    | Rol                  | Ámbito / Funcionalidad |
|--------------------------------------|--------------|----------------------|------------------------|
| beto.caleb.delgado.rojas@gmail.com   | Admin1234*   | Admin Centro         | SuperAdmin y Administración del Centro |
| admin@centroesperanza.com            | Admin1234*   | Admin Centro         | Gestión de Centro, Usuarios y Roles |
| recepcion@centroesperanza.com        | Recep1234*   | Recepcionista        | Pacientes, Expedientes y Agenda |
| carlos.mendoza@centroesperanza.com   | Psicologo123*| Psicólogo Especialista| TCC y Clínica (BOB 180.00), Citas y Teleconsulta |
| mariana.vargas@centroesperanza.com   | Psicologo123*| Psicólogo Especialista| Familiar e Infantil (BOB 200.00), Citas y Teleconsulta |
| juan.perez@paciente.com              | Paciente123* | Paciente Adulto      | Expediente EXP-2026-001 (CI: 8472910-LP) |
| mateo.quispe@paciente.com            | Paciente123* | Paciente Menor       | Expediente EXP-2026-003 (Tutora: Beatriz Lima) |

### Gabinete MenteSana (`mentesana`)

| Email                       | Contraseña   | Rol                  | Ámbito |
|-----------------------------|-------------|----------------------|--------|
| admin@mentesana.com         | Admin1234*  | Admin Centro         | Gestión Centro |
| psicologo@mentesana.com     | Psico1234*  | Psicólogo            | Terapeuta |
| recepcion@mentesana.com     | Recep1234*  | Recepcionista        | Recepción |
| coordinador@mentesana.com   | Coord1234*  | Coordinador Clínico  | Supervisión |

> **Requisitos de contraseña:** Mínimo 8 caracteres, al menos 1 mayúscula, 1 número y 1 carácter especial.

---

## 8. Endpoints de la API

### Autenticación (Public + Tenant)

| Método | Endpoint                           | Acceso     | Descripción                               |
|--------|------------------------------------|------------|-------------------------------------------|
| POST   | `/api/auth/register/`              | Público    | Registrar nuevo usuario                   |
| POST   | `/api/auth/login/`                 | Público    | Login → JWT (con auto-resolución de tenant) |
| POST   | `/api/auth/logout/`                | Auth       | Logout → blacklist refresh token          |
| GET    | `/api/auth/me/`                    | Auth       | Perfil del usuario autenticado            |
| POST   | `/api/auth/password-reset/`        | Público    | Solicitar token de recuperación           |
| POST   | `/api/auth/password-reset-confirm/`| Público    | Confirmar nueva contraseña con token      |

### Tenants / Centros

| Método | Endpoint                     | Acceso     | Descripción                               |
|--------|------------------------------|------------|-------------------------------------------|
| GET    | `/api/tenants/`              | Público    | Listar todos los centros                  |
| GET    | `/api/tenants/public/`       | Público    | Listar centros activos (selector login)   |
| POST   | `/api/tenants/`              | SuperAdmin | Crear nuevo centro + esquema PostgreSQL   |
| PUT    | `/api/tenants/{id}/`         | SuperAdmin | Editar centro                             |
| POST   | `/api/tenants/{id}/suspender/`| SuperAdmin| Suspender centro                          |
| POST   | `/api/tenants/{id}/activar/` | SuperAdmin | Reactivar centro                          |

### Usuarios y Roles (dentro del Tenant)

> **Header requerido:** `X-Tenant-ID: <slug_del_centro>` (o resuelto automáticamente por el JWT)

| Método | Endpoint                            | Acceso       | Descripción                        |
|--------|-------------------------------------|--------------|------------------------------------|
| GET    | `/api/users/`                       | Admin Centro | Listar usuarios del centro         |
| POST   | `/api/users/`                       | Admin Centro | Crear usuario en el centro         |
| PUT/PATCH | `/api/users/{id}/`               | Admin Centro | Editar usuario (sin exigir email)  |
| POST   | `/api/users/{id}/alternar_estado/`  | Admin Centro | Activar/desactivar usuario         |
| GET    | `/api/roles/`                       | Admin Centro | Listar roles del sistema RBAC      |
| POST   | `/api/roles/`                       | Admin Centro | Crear rol con permisos             |
| GET    | `/api/permisos/`                    | Auth         | Listar permisos disponibles        |

### Clínica y Directorio Profesional (Sprint 1)

| Método | Endpoint                                    | Acceso       | Descripción                                         |
|--------|---------------------------------------------|--------------|-----------------------------------------------------|
| GET    | `/api/clinica/especialidades/`              | Auth         | Listar especialidades clínicas disponibles          |
| GET    | `/api/clinica/psicologos/`                  | Auth         | Directorio de psicólogos con tarifas y colegiatura  |
| POST   | `/api/clinica/psicologos/`                  | Admin Centro | Alta de psicólogo con aranceles y especialidades    |
| PUT/PATCH | `/api/clinica/psicologos/{id}/`          | Admin Centro | Actualizar honorarios y perfil profesional          |
| GET/POST | `/api/clinica/psicologos/{id}/disponibilidad/` | Auth/Admin| Configurar franjas horarias semanales de atención   |
| GET    | `/api/clinica/pacientes/`                   | Clínico      | Listar pacientes y expedientes clínicos             |
| POST   | `/api/clinica/pacientes/`                   | Clínico      | Alta de paciente (código `EXP-YYYYMM-XXXX`, tutores)|
| PUT/PATCH | `/api/clinica/pacientes/{id}/`           | Clínico      | Editar datos del paciente y tutor                   |
| GET    | `/api/clinica/pacientes/me/`                | Paciente     | Expediente clínico del paciente autenticado         |

### Agenda, Citas, Teleconsulta y KPIs (Sprint 1)

| Método | Endpoint                                    | Acceso       | Descripción                                         |
|--------|---------------------------------------------|--------------|-----------------------------------------------------|
| GET    | `/api/agenda/citas/slots-disponibles/`      | Auth         | Matriz de intervalos libres calculados (50 minutos) |
| GET    | `/api/agenda/citas/`                        | Auth         | Listar citas con filtros (psicólogo, fecha, estado) |
| POST   | `/api/agenda/citas/`                        | Auth         | Reserva de cita con bloqueo concurrente pesimista   |
| POST   | `/api/agenda/citas/{id}/cancelar/`          | Auth         | Cancelar cita (valida anticipación de 2 horas)      |
| GET    | `/api/agenda/citas/calendario/`             | Auth         | Matriz de eventos formateada para FullCalendar      |
| GET    | `/api/agenda/teleconsulta/{cita_id}/access/`| Auth         | Sala Jitsi Meet + token JWT (Moderador / Invitado)  |
| POST   | `/api/agenda/teleconsulta/{cita_id}/finish/`| Psicólogo    | Finalizar videollamada y registrar duración real    |
| GET    | `/api/agenda/dashboard/kpis/`               | Coordinador  | Dashboard clínico (ocupación, ausentismo, ingresos) |
| GET    | `/api/agenda/alertas/`                      | Clínico      | Listar alertas tempranas por inasistencia reiterada |
| POST   | `/api/agenda/alertas/{id}/resolver/`        | Clínico      | Marcar alerta como resuelta con nota de seguimiento |

---

## 9. Solución de Problemas Comunes

### Backend

| Problema | Causa | Solución |
|----------|-------|----------|
| `FATAL: database "sigepsi_db" does not exist` | No se creó la BD | Ejecutar `CREATE DATABASE sigepsi_db;` en psql |
| `psycopg2.OperationalError: could not connect` | PostgreSQL no activo | Iniciar servicio PostgreSQL |
| `No module named 'django'` | Entorno virtual no activo | Ejecutar `.\venv\Scripts\Activate.ps1` |
| `relation "tenants_tenant" does not exist` | Falta migrar | Ejecutar `python manage.py migrate_schemas --shared` |
| `TenantNotFoundError` en tests | Falta datos semilla | Ejecutar `python manage.py seed_data` y `seed_sprint1` |
| Error en edición: `email requerido` | PUT con partial=False | Usar PATCH o vistas DRF actualizadas con `partial=True` |

### Web (Angular)

| Problema | Causa | Solución |
|----------|-------|----------|
| `npm ERR! ERESOLVE` | Conflicto de dependencias | Ejecutar `npm install --legacy-peer-deps` |
| `ng: command not found` | Angular CLI no instalado | Ejecutar `npm install -g @angular/cli` o usar `npx ng serve` |
| Error CORS en el navegador | Backend no corriendo | Asegurar que el backend corra en `localhost:8000` |
| No aparecen los slots en agenda | Formato respuesta anidado | Servicio ya actualizado para desempaquetar `{ slots: [...] }` |

### Móvil (Flutter / Android)

| Problema | Causa | Solución |
|----------|-------|----------|
| `Gradle requires JVM 17 or later to run. Your build is currently configured to use JVM 8` | PATH de Windows tiene Java 8 antes de Android Studio JBR | Agregar `org.gradle.java.home=C:/Program Files/Android/Android Studio/jbr` en `C:\Users\User\.gradle\gradle.properties` |
| `Connection refused` en emulador | URL incorrecta | Usar `10.0.2.2` en vez de `localhost` para emulador Android |
| `Connection refused` en celular físico | Falta redirección de puerto | Ejecutar `adb reverse tcp:8000 tcp:8000` con cable USB conectado |
| `Cleartext HTTP not permitted` (Android) | Seguridad Android | `android:usesCleartextTraffic="true"` ya configurado en `AndroidManifest.xml` |

---

## 🏁 Resumen de Comandos Rápidos

```powershell
# ═══════════════════ BACKEND ═══════════════════
cd prototipo\backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt                # Instalar dependencias
python manage.py migrate_schemas --shared      # Migraciones public
python manage.py migrate_schemas --tenant      # Migraciones tenants (incluye clinica y agenda)
python manage.py seed_data                     # Datos de prueba Sprint 0
python manage.py seed_sprint1                  # Datos clínicos y citas Sprint 1
python manage.py runserver                     # Servidor → :8000
python verify_sprint0.py                       # Verificación Sprint 0 (25 pruebas)
python verify_sprint1.py                       # Verificación Sprint 1 (24 pruebas)
python scratch\verify_all_use_cases.py         # Verificación integral Casos de Uso (36/36)

# ═══════════════════ WEB ═══════════════════════
cd prototipo\web
npm install                                    # Instalar dependencias
npm start                                      # Servidor desarrollo → :4200
npm run build                                  # Build producción (0 errores)

# ═══════════════════ MÓVIL ═════════════════════
cd prototipo\movil
flutter pub get                                # Instalar paquetes Dart
flutter run                                    # Ejecutar en emulador / celular USB
flutter run -d chrome                          # Ejecutar como Web
flutter build apk --release                    # Compilar APK producción

# ═══════════════════ DOCKER & RENDER ═══════════════
cd prototipo
docker compose up -d --build                   # Orquestación completa local (DB, Backend, Web)
docker compose ps                              # Estado de contenedores
docker compose logs -f backend                 # Logs del backend
docker compose down                            # Detener contenedores
# Despliegue en Render: Ver DESPLIEGUE_RENDER.md o usar render.yaml con Blueprint
```

