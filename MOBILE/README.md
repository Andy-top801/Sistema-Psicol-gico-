# Explicación de la Aplicación Móvil (SIGEPSI)

Aplicación móvil construida en **Flutter (Dart)**, orientada a los pacientes, tal como define `DOCUMENTACIÓN/CONTEXTO_PROYECTO_SIGEPSI.md` (secciones 7.6 y 9.1). Consume la misma API REST (Django + DRF + JWT) que ya usa el `FRONTEND` web.

## Estado actual: Sprint 0 (CU2 y CU27)

Esta primera versión implementa lo que corresponde a Sprint 0 en la app móvil: **CU2 — Gestionar inicio de sesión y autenticación** (HU-01/02/09: registro, login, sesión) y **CU27 — Recuperar contraseña o credenciales de acceso** (HU-10 / RF-31). El resto de la app está reservado para sprints posteriores.

## Organización de `lib/`

```
lib/
  core/       # infraestructura transversal: config de API, cliente HTTP, storage seguro de tokens
  shell/      # navegación de la app no ligada a un paquete de negocio (splash, home)
  paquetes/   # módulos de negocio, organizados igual que FRONTEND/src/app/modules/
```

`core/` y `shell/` no son "paquetes" en el sentido de Scrum/CU — son infraestructura y navegación que cualquier paquete de negocio necesita.

## Los 6 paquetes (igual que en `FRONTEND`)

La app web Angular está dividida en 6 paquetes/módulos (`CONTEXTO_PROYECTO_SIGEPSI.md`, sección 3.10 "Paquetes y Casos de Uso"). La app móvil refleja la misma división dentro de `lib/paquetes/`, para que ambas plataformas compartan la misma arquitectura de módulos:

| Carpeta | Paquete | Casos de Uso | Estado |
|---|---|---|---|
| `paquete1_admin_seguridad/` | Administración, Seguridad y Multi-Tenant | CU1-CU5, **CU27** | **Implementado (CU2 y CU27)** |
| `paquete2_gestion_clinica/` | Gestión Clínica y de Profesionales | CU6-CU8, CU15, CU16, CU19 | Reservado (ver su `README.md`) |
| `paquete3_agenda_comunicacion/` | Agenda, Comunicación y Seguimiento | CU9-CU13, CU17 | Reservado (ver su `README.md`) |
| `paquete4_formularios/` | Formularios, Consentimientos y Documentación | CU14, CU18 | Reservado (ver su `README.md`) |
| `paquete5_inteligencia_artificial/` | Inteligencia Artificial y Chatbot | CU20-CU24 | Reservado (ver su `README.md`) |
| `paquete6_reportes_pagos/` | Reportes y Pagos | CU25, CU26 | Reservado (ver su `README.md`) |

Los paquetes 2 a 6 solo contienen un `README.md` documentando qué cubrirán — deliberadamente no tienen código, para no implementar funcionalidad fuera del alcance actual.

## `paquete1_admin_seguridad/` — carpetas por tipo, igual que `FRONTEND`

Mismo patrón que `FRONTEND/src/app/modules/paquete1_admin_seguridad/` (`components/`, `services/`): dentro del paquete, las carpetas son por **tipo** (`models/`, `services/`, `providers/`, `screens/`, `widgets/`), no una carpeta por caso de uso. Un mismo `services/`, por ejemplo, contiene tanto el código de CU2 como el de CU27. Ver el `README.md` del paquete para la tabla completa archivo → CU:

- `models/` — `Usuario`, `AuthTokens` (CU2).
- `services/` — `auth_service.dart` (CU2: login, registro, refresh, perfil, logout — `/api/users/auth/login/`, `/auth/register/`, `/auth/refresh/`, `/me/`) y `password_reset_service.dart` (CU27: `/api/users/auth/password-reset/`, `/password-reset-confirm/`).
- `providers/` — `auth_provider.dart` (CU2: estado de sesión observable con `provider`).
- `screens/` — `LoginScreen`, `RegisterScreen` (CU2); `ForgotPasswordScreen`, `ResetPasswordScreen` (CU27).
- `widgets/` (no es un CU) — `AuthHeader`, `AuthTextField`, `GradientButton`: la marca visual compartida por las pantallas de ambos CU.

## Configuración de red

El backend resuelve el centro psicológico (tenant) según el dominio de la petición (`django-tenants`). Por eso la URL base de la API (`lib/core/config/api_config.dart`) apunta por defecto a la clínica de prueba creada por `python manage.py init_system`: `http://sanamente.localhost:8000/api`.

Para apuntar a otro entorno sin tocar código:

```bash
flutter run --dart-define=API_BASE_URL=http://sanamente.localhost:8000/api
```

**Nota para emulador Android:** `sanamente.localhost` no resuelve al equipo anfitrión dentro del emulador. Usa `adb reverse tcp:8000 tcp:8000` (mantiene el dominio) o `--dart-define=API_BASE_URL=http://10.0.2.2:8000/api`. En simulador iOS, `sanamente.localhost` funciona directo.

## Correr los tests

```bash
cd MOBILE
flutter test
```
