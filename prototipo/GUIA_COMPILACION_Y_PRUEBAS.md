# 📘 Guía de Compilación, Ejecución y Pruebas — SIGEPSI Prototipo (Sprint 0)

> **Proyecto:** SIGEPSI — Sistema de Gestión para Centros Psicológicos  
> **Arquitectura:** Backend (Django REST + Multi-Tenant) · Web (Angular 17) · Móvil (Flutter)  
> **Base de Datos:** PostgreSQL (requerido para multi-tenancy)

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

| Herramienta   | Versión Mínima | Verificar con            |
|---------------|----------------|--------------------------|
| Python        | 3.10+          | `python --version`       |
| PostgreSQL    | 14+            | `psql --version`         |
| Node.js       | 18+            | `node --version`         |
| npm           | 9+             | `npm --version`          |
| Angular CLI   | 17+            | `ng version`             |
| Flutter SDK   | 3.0+           | `flutter --version`      |
| Dart SDK      | 3.0+           | `dart --version`         |
| Git           | 2.x            | `git --version`          |

---

## 2. Jerarquía de Roles y Arquitectura de Usuarios

En SIGEPSI, la arquitectura multi-tenant divide la responsabilidad en dos planos bien diferenciados: **Nivel Plataforma Global (SaaS)** y **Nivel Centro Psicológico (Tenant)**.

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                   NIVEL 0: PLATAFORMA GLOBAL (Esquema: public)                    ║
║                                                                                   ║
║  👑 SuperAdmin (admin@sigepsi.com)                                                ║
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
├── tests/                # Tests unitarios (pytest/django-tenants)
├── manage.py
├── requirements.txt
└── verify_sprint0.py     # Script de verificación integral Sprint 0
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

### 3.4 Migraciones y Base de Datos

```powershell
# Migrar esquema public (compartido entre todos los tenants)
python manage.py migrate_schemas --shared

# Migrar esquemas de tenants
python manage.py migrate_schemas --tenant
```

> **Nota:** `django-tenants` reemplaza el comando `migrate` estándar con `migrate_schemas`.

### 3.5 Sembrar Datos de Prueba

```powershell
# Ejecutar el comando de siembra de datos
python manage.py seed_data
```

Este comando crea automáticamente:
- ✅ **Tenant `public`** con dominio `localhost`
- ✅ **SuperAdmin Global:** `admin@sigepsi.com` / `Admin1234*`
- ✅ **Centro "Esperanza"** (tenant: `centro_esperanza`)
- ✅ **Centro "MenteSana"** (tenant: `mentesana`)
- ✅ **Roles:** Admin Centro, Coordinador, Psicólogo, Recepcionista, Paciente
- ✅ **12 permisos** asignados por rol (RBAC)
- ✅ **Usuarios demo** en cada centro con diferentes roles

### 3.6 Ejecutar el Servidor Backend

```powershell
# Iniciar servidor de desarrollo (puerto 8000)
python manage.py runserver
```

El servidor quedará disponible en: **http://localhost:8000**

Verificar que funciona abriendo en el navegador:
- `http://localhost:8000/api/tenants/public/` → Lista de centros públicos

### 3.7 Ejecutar Tests del Backend

#### Tests unitarios con Django TestRunner

```powershell
# Ejecutar TODOS los tests
python manage.py test tests --verbosity=2

# Tests específicos por módulo:
python manage.py test tests.test_auth --verbosity=2              # Autenticación y JWT
python manage.py test tests.test_multitenant --verbosity=2       # Multi-tenancy y aislamiento
python manage.py test tests.test_users_roles --verbosity=2       # Usuarios, roles y RBAC
```

> **Importante:** Los tests usan `TenantTestCase` de `django-tenants`, que crea automáticamente un tenant temporal y su esquema para cada test. Requiere PostgreSQL activo.

#### Script de verificación integral (Sprint 0)

```powershell
# Ejecutar el plan de pruebas completo (25 casos de prueba)
python verify_sprint0.py
```

Este script ejecuta los **25 casos de prueba del Sprint 0** (TP-01 a TP-25):

| ID      | HU    | Descripción                                          |
|---------|-------|------------------------------------------------------|
| TP-01   | HU-01 | Registrar usuario con datos válidos                  |
| TP-02   | HU-01 | Registrar con correo duplicado (rechazado)           |
| TP-03   | HU-01 | Registrar con contraseña débil (rechazado)           |
| TP-04   | HU-02 | Login con credenciales correctas → JWT               |
| TP-05   | HU-02 | Login con credenciales incorrectas → error           |
| TP-06   | HU-02 | Login con cuenta suspendida → bloqueado              |
| TP-07   | HU-03 | Alta de centro con esquema PostgreSQL aislado        |
| TP-08   | HU-03 | Alta de centro con nombre duplicado (bloqueado)      |
| TP-09   | HU-04 | Editar configuración institucional del centro        |
| TP-10   | HU-05 | Registrar usuario dentro del centro                  |
| TP-11   | HU-05 | Registrar con correo duplicado en centro             |
| TP-12   | HU-06 | Asignación de rol a usuario                          |
| TP-13   | HU-06 | Cambiar rol de usuario                               |
| TP-14   | HU-06 | Verificación RBAC de permisos por rol                |
| TP-15   | HU-07 | Consultar datos solo dentro de esquema propio        |
| TP-16   | HU-07 | Acceso cruzado entre tenants bloqueado               |
| TP-17   | HU-07 | Esquemas PostgreSQL completamente separados          |
| TP-18   | HU-08 | Editar datos de centro suscrito                      |
| TP-19   | HU-08 | Suspender centro desactiva acceso                    |
| TP-20   | HU-08 | Dar de baja centro suscrito                          |
| TP-21   | HU-09 | Cerrar sesión invalida token (blacklist)             |
| TP-22   | HU-09 | Acceso posterior bloqueado tras logout               |
| TP-23   | HU-10 | Solicitud de recuperación genera token temporal      |
| TP-24   | HU-10 | Restablecer contraseña con token válido              |
| TP-25   | HU-10 | Uso de token ya consumido es rechazado               |

> **Prerequisito:** El script requiere que `seed_data` se haya ejecutado previamente para tener los tenants `centro_esperanza` y `mentesana` con sus datos.

---

## 4. Web (Angular 17)

### 4.1 Estructura del Frontend Web

```
web/
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── guards/          # Auth guards (authGuard, superAdminGuard, adminCentroGuard)
│   │   │   ├── interceptors/    # HTTP interceptor (JWT + X-Tenant-ID)
│   │   │   ├── models/          # Interfaces TypeScript
│   │   │   └── services/        # AuthService, TenantService, UserService, etc.
│   │   ├── layout/              # MainLayoutComponent (sidebar + contenido)
│   │   ├── modules/
│   │   │   ├── auth/            # Login y Password Reset
│   │   │   ├── dashboard/       # Panel principal
│   │   │   ├── tenants/         # CRUD de centros (SuperAdmin)
│   │   │   ├── users/           # CRUD de usuarios
│   │   │   ├── roles/           # CRUD de roles y permisos
│   │   │   └── centro/          # Configuración institucional
│   │   ├── app.component.ts
│   │   ├── app.config.ts
│   │   └── app.routes.ts
│   ├── styles.css               # Estilos globales
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
- Angular 17.3 (Standalone Components, Signals)
- TypeScript 5.4
- RxJS 7.8

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

### 4.6 Probar la Web Manualmente

1. Abrir `http://localhost:4200/login`
2. Seleccionar un centro de la lista desplegable (ej: "Centro Psicológico Esperanza")
3. Ingresar credenciales (ver [Credenciales de Prueba](#7-credenciales-de-prueba))
4. Navegar por los módulos del dashboard:

| Ruta             | Módulo                     | Requiere Rol          |
|------------------|----------------------------|-----------------------|
| `/dashboard`     | Panel principal            | Cualquier autenticado |
| `/tenants`       | Gestión de centros         | SuperAdmin            |
| `/users`         | CRUD de usuarios           | Admin Centro          |
| `/roles`         | CRUD de roles/permisos     | Admin Centro          |
| `/centro`        | Configuración del centro   | Admin Centro          |

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

### 5.2 Instalar Dependencias y Generar Plataforma Nativa

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

| Email              | Contraseña   | Rol        |
|--------------------|-------------|------------|
| admin@sigepsi.com  | Admin1234*  | SuperAdmin |

### Centro Psicológico Esperanza (`centro_esperanza`)

| Email                           | Contraseña   | Rol                  |
|---------------------------------|-------------|----------------------|
| admin@centroesperanza.com       | Admin1234*  | Admin Centro         |
| psicologo@centroesperanza.com   | Psico1234*  | Psicólogo            |
| recepcion@centroesperanza.com   | Recep1234*  | Recepcionista        |
| coordinador@centroesperanza.com | Coord1234*  | Coordinador Clínico  |

### Gabinete MenteSana (`mentesana`)

| Email                       | Contraseña   | Rol                  |
|-----------------------------|-------------|----------------------|
| admin@mentesana.com         | Admin1234*  | Admin Centro         |
| psicologo@mentesana.com     | Psico1234*  | Psicólogo            |
| recepcion@mentesana.com     | Recep1234*  | Recepcionista        |
| coordinador@mentesana.com   | Coord1234*  | Coordinador Clínico  |

> **Requisitos de contraseña:** Mínimo 8 caracteres, al menos 1 mayúscula, 1 número y 1 carácter especial.

---

## 8. Endpoints de la API

### Autenticación (Public + Tenant)

| Método | Endpoint                           | Acceso     | Descripción                               |
|--------|------------------------------------|------------|-------------------------------------------|
| POST   | `/api/auth/register/`              | Público    | Registrar nuevo usuario                   |
| POST   | `/api/auth/login/`                 | Público    | Login → JWT (access + refresh)            |
| POST   | `/api/auth/logout/`                | Auth       | Logout → blacklist refresh token          |
| GET    | `/api/auth/me/`                    | Auth       | Perfil del usuario autenticado            |
| POST   | `/api/auth/password-reset/`        | Público    | Solicitar token de recuperación           |
| POST   | `/api/auth/password-reset-confirm/`| Público    | Confirmar nueva contraseña con token      |

### Tenants / Centros

| Método | Endpoint                     | Acceso     | Descripción                               |
|--------|------------------------------|------------|-------------------------------------------|
| GET    | `/api/tenants/`              | Público    | Listar todos los centros                  |
| GET    | `/api/tenants/public/`       | Público    | Listar centros activos (selector login)   |
| POST   | `/api/tenants/`              | SuperAdmin | Crear nuevo centro + esquema              |
| PUT    | `/api/tenants/{id}/`         | SuperAdmin | Editar centro                             |
| POST   | `/api/tenants/{id}/suspender/`| SuperAdmin| Suspender centro                          |
| POST   | `/api/tenants/{id}/activar/` | SuperAdmin | Reactivar centro                          |

### Usuarios y Roles (dentro del Tenant)

> **Header requerido:** `X-Tenant-ID: <slug_del_centro>`

| Método | Endpoint                            | Acceso       | Descripción                        |
|--------|-------------------------------------|--------------|------------------------------------|
| GET    | `/api/users/`                       | Admin Centro | Listar usuarios del centro         |
| POST   | `/api/users/`                       | Admin Centro | Crear usuario en el centro         |
| PUT    | `/api/users/{id}/`                  | Admin Centro | Editar usuario                     |
| POST   | `/api/users/{id}/alternar_estado/`  | Admin Centro | Activar/desactivar usuario         |
| GET    | `/api/roles/`                       | Admin Centro | Listar roles                       |
| POST   | `/api/roles/`                       | Admin Centro | Crear rol con permisos             |
| GET    | `/api/permisos/`                    | Auth         | Listar permisos disponibles        |

### Configuración del Centro

| Método | Endpoint                | Acceso       | Descripción                           |
|--------|-------------------------|--------------|---------------------------------------|
| GET    | `/api/centro/config/`   | Admin Centro | Ver configuración institucional       |
| PUT    | `/api/centro/config/`   | Admin Centro | Editar configuración institucional    |

### Ejemplo de petición con cURL

```bash
# Login en un centro específico
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: centro_esperanza" \
  -d '{"email": "admin@centroesperanza.com", "password": "Admin1234*"}'

# Usar el token obtenido para consultar usuarios
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer <access_token>" \
  -H "X-Tenant-ID: centro_esperanza"
```

---

## 9. Solución de Problemas Comunes

### Backend

| Problema | Causa | Solución |
|----------|-------|----------|
| `FATAL: database "sigepsi_db" does not exist` | No se creó la BD | Ejecutar `CREATE DATABASE sigepsi_db;` en psql |
| `psycopg2.OperationalError: could not connect` | PostgreSQL no activo | Iniciar servicio PostgreSQL |
| `No module named 'django'` | Entorno virtual no activo | Ejecutar `.\venv\Scripts\Activate.ps1` |
| `relation "tenants_tenant" does not exist` | Falta migrar | Ejecutar `python manage.py migrate_schemas --shared` |
| `TenantNotFoundError` en verify_sprint0.py | Falta datos semilla | Ejecutar `python manage.py seed_data` primero |
| Error en tests: `role "test_" already exists` | Esquema temporal residual | Reiniciar PostgreSQL o eliminar esquemas huérfanos |

### Web (Angular)

| Problema | Causa | Solución |
|----------|-------|----------|
| `npm ERR! ERESOLVE` | Conflicto de dependencias | Ejecutar `npm install --legacy-peer-deps` |
| `ng: command not found` | Angular CLI no instalado | Ejecutar `npm install -g @angular/cli` o usar `npx ng serve` |
| Error CORS en el navegador | Backend no corriendo | Asegurar que el backend corra en `localhost:8000` |
| Pantalla en blanco en login | Sin centros cargados | Ejecutar `seed_data` en el backend |

### Móvil (Flutter)

| Problema | Causa | Solución |
|----------|-------|----------|
| `Connection refused` en emulador | URL incorrecta | Usar `10.0.2.2` en vez de `localhost` para emulador Android |
| `flutter pub get` falla | SDK no compatible | Verificar `flutter doctor` y actualizar SDK |
| App no conecta al backend | Firewall o red | Verificar que el backend esté accesible desde el dispositivo |
| `Cleartext HTTP not permitted` (Android) | Seguridad Android | Agregar `android:usesCleartextTraffic="true"` en `AndroidManifest.xml` |

---

## 🏁 Resumen de Comandos Rápidos

```powershell
# ═══════════════════ BACKEND ═══════════════════
cd prototipo\backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt           # Instalar dependencias
python manage.py migrate_schemas --shared # Migraciones public
python manage.py migrate_schemas --tenant # Migraciones tenants
python manage.py seed_data                # Datos de prueba
python manage.py runserver                # Servidor → :8000
python manage.py test tests -v2          # Tests unitarios
python verify_sprint0.py                  # Verificación Sprint 0

# ═══════════════════ WEB ═══════════════════════
cd prototipo\web
npm install                               # Instalar dependencias
npm start                                 # Servidor → :4200
npm run build                             # Build producción

# ═══════════════════ MÓVIL ═════════════════════
cd prototipo\movil
flutter pub get                           # Instalar dependencias
flutter run                               # Ejecutar en emulador/device
flutter run -d chrome                     # Ejecutar como web
flutter build apk --release               # Compilar APK
flutter test                              # Tests unitarios
```
