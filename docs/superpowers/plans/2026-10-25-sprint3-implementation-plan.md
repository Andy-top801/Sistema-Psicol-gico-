# Sprint 3 - Implementación de Experiencia Móvil de Pacientes y Motores de IA Asistiva

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar y verificar el código completo del Sprint 3 de SIGEPSI abarcando la experiencia móvil nativa en Flutter (autenticación JWT persistente, consulta y cancelación de citas >24h, teleconsulta WebRTC, entrega de tareas y Mood Tracker), las notificaciones automáticas push FCM (CU12), y los motores de IA para triaje/crisis (CU21) y recomendación multivariable de terapeutas con validación humana HITL (CU22) en backend Django REST y frontend web Angular 17.

**Architecture:** Arquitectura modular multi-tenant desacoplada en 3 capas. Capa de persistencia con esquemas PostgreSQL 16 aislados por clínica psicológica y nuevos modelos relacionales (`comunicacion_tokenfcm`, `agenda_notificacioncita`, `clinica_registroanimo`, `clinica_clasificacionia`, `clinica_sugerenciamatching`). Capa de lógica de negocio en Django REST con servicios especializados (`ClasificadorMotivoConsulta`, `MatchingPsicologoService`, `FCMNotificationService`) y validación estricta de reglas clínicas/temporales. Capa de presentación multiplataforma en Flutter 3.x (cliente móvil) y Angular 17 (consola de triaje web).

**Tech Stack:** Python 3.13, Django 5.x REST Framework, `django-tenants`, PostgreSQL 16, Flutter 3.47 / Dart 3.13, Angular 17 Standalone, Firebase Cloud Messaging (FCM v1), Jitsi Meet WebRTC.

**Spec:** [documentacion/sprint3.md](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/documentacion/sprint3.md)

## Global Constraints

- Backend implementado sobre el entorno virtual existente `prototipo/backend/venv` con `django_tenants.postgresql_backend`.
- Aislamiento multi-tenant estricto: todas las operaciones clínicas y de citas deben resolverse dentro del esquema del tenant activo (`schema_context(tenant.schema_name)`).
- Regla de cancelación estricta: sólo se permite cancelación autónoma de cita si $\Delta t > 24\text{ horas}$; si $\Delta t \le 24\text{h}$, retornar HTTP 400 Bad Request con código `CANCELLATION_WINDOW_EXPIRED`.
- Salvaguarda ética obligatoria de IA (*Human-in-the-Loop*): la sugerencia de asignación de psicólogo (CU22) nunca se aplica de forma autónoma a la base de datos; requiere confirmación explícita del Coordinador Clínico.
- Detección perentoria de crisis en IA (CU21): ante indicadores de riesgo vital o autolesión, activar `alerta_crisis = True` y severidad `CRITICA`.
- Anonimización obligatoria de datos personales (PII) antes de cualquier inferencia de lenguaje natural.
- Coherencia con los 7 diagramas de secuencia BCE de Sprint 3 (IDs EA: 306, 307, 308, 309, 310, 311, 312).

## Review Focus

1. **Intento de cancelación con exactamente 24h o menos:** El backend debe bloquear la operación con código `CANCELLATION_WINDOW_EXPIRED` independientemente del reloj del dispositivo cliente.
2. **Registro de estado de ánimo duplicado en la misma fecha:** El backend debe asegurar unicidad (`uq_registroanimo_paciente_fecha`) actualizando el registro existente o respondiendo con conflicto según la intención.
3. **Inferencia de intake con expresiones complejas de crisis vital:** El motor debe capturar variantes léxicas ('morir', 'acabar con todo', 'no quiero vivir') sin falsos negativos y levantar la bandera roja de triaje.
4. **Matching de terapeutas con psicólogo sobrecargado (100% capacidad):** El terapeuta con carga máxima debe recibir 0 puntos en el factor de balanceo de carga y no liderar el ranking.
5. **Token FCM inválido o paciente sin dispositivo:** El servicio push no debe arrojar excepciones no controladas ni interrumpir la transacción principal de agenda.

---

### Task 1: Modelos de Datos Relacionales del Sprint 3 en Backend (PostgreSQL Multi-Tenant)

**Files:**
- Modify: `prototipo/backend/clinica/models.py`
- Modify: `prototipo/backend/agenda/models.py`
- Create: `prototipo/backend/comunicacion/models.py` (o extensión en `clinica/models.py` y `agenda/models.py`)
- Create: `prototipo/backend/clinica/migrations/0002_sprint3_models.py` (vía `makemigrations`)
- Test: `prototipo/backend/tests/test_sprint3_models.py`

**Interfaces:**
- Consumes: `clinica.models.Paciente`, `clinica.models.Psicologo`, `agenda.models.Cita`, `clinica.models.RespuestaPreConsulta`
- Produces:
  - `TokenFCM(paciente, token, plataforma, activo, creado_en)`
  - `NotificacionCita(cita, tipo_evento, canal, enviada, fecha_programada, fecha_envio)`
  - `RegistroAnimo(paciente, fecha_registro, estado_animo, escala_valor, factores_contexto, nota_reflexiva)`
  - `ClasificacionIA(respuestapreconsulta, categoria_principal, confianza_score, nivel_severidad, alerta_crisis, palabras_clave_detectadas, explicacion_heuristica, hash_trazabilidad_sha256)`
  - `SugerenciaMatching(paciente, clasificacion, psicologo_sugerido, ranking_posicion, score_afinidad, factores_ponderacion, estado_decision, validado_por_coordinador, justificacion_clinica)`

- [ ] **Step 1: Escribir prueba unitaria que verifica la existencia y restricciones de las 5 entidades de Sprint 3**
- [ ] **Step 2: Ejecutar prueba para verificar que falla por falta de modelos**
  Run: `prototipo\backend\venv\Scripts\python.exe -m pytest prototipo/backend/tests/test_sprint3_models.py`
- [ ] **Step 3: Implementar los modelos Django ORM con sus campos, llaves foráneas y restricciones UNIQUE**
- [ ] **Step 4: Generar y aplicar migraciones en los esquemas multi-tenant**
  Run: `prototipo\backend\venv\Scripts\python.exe prototipo/backend/manage.py makemigrations`
  Run: `prototipo\backend\venv\Scripts\python.exe prototipo/backend/manage.py migrate_schemas`
- [ ] **Step 5: Ejecutar la prueba unitaria y confirmar que pasa al 100%**

---

### Task 2: Motor de Clasificación Asistida por IA y Detección de Crisis (CU21 / HU-47)

**Files:**
- Modify: `prototipo/backend/clinica/ia_rules_engine.py`
- Modify: `prototipo/backend/clinica/views.py`
- Modify: `prototipo/backend/clinica/urls.py`
- Test: `prototipo/backend/tests/test_sprint3_clasificacion_ia.py`

**Interfaces:**
- Consumes: Texto de motivo de consulta, síntomas principales, escala de urgencia percibida
- Produces: `ClasificadorMotivoConsulta.clasificar(motivo, sintomas, urgencia) -> Dict[str, Any]`
- Endpoint: `POST /api/v1/clinica/intake/{id}/clasificar/` y `GET /api/v1/clinica/triaje/alertas/`

- [ ] **Step 1: Escribir pruebas unitarias de clasificación NLP, sanitización PII y detección de patrones de crisis**
- [ ] **Step 2: Ejecutar prueba y verificar que falla**
- [ ] **Step 3: Implementar la clase `ClasificadorMotivoConsulta` en `ia_rules_engine.py` con sanitización PII, análisis léxico-semántico de 5 áreas, banderas de crisis e inmutabilidad con SHA-256**
- [ ] **Step 4: Implementar vistas REST y endpoints en `clinica/views.py` y registrar rutas en `clinica/urls.py`**
- [ ] **Step 5: Ejecutar pruebas y confirmar aprobación**

---

### Task 3: Algoritmo Multivariable de Emparejamiento de Psicólogos con Validación Humana HITL (CU22 / HU-48)

**Files:**
- Modify: `prototipo/backend/clinica/ia_rules_engine.py`
- Modify: `prototipo/backend/clinica/views.py`
- Modify: `prototipo/backend/clinica/urls.py`
- Test: `prototipo/backend/tests/test_sprint3_matching.py`

**Interfaces:**
- Consumes: Especialidad requerida, modalidad de atención, queryset de psicólogos del tenant
- Produces: `MatchingPsicologoService.sugerir_psicologos(especialidad_req, modalidad_req, psicologos_qs) -> List[Dict]`
- Endpoints:
  - `POST /api/v1/clinica/triaje/{paciente_id}/sugerir-matching/` (Genera Top 3)
  - `GET /api/v1/clinica/triaje/{paciente_id}/sugerencias/` (Lista Top 3)
  - `POST /api/v1/clinica/triaje/asignar/` (Aprobación humana HITL)

- [ ] **Step 1: Escribir pruebas del algoritmo ponderado (40% especialidad, 30% horarios, 20% carga, 10% modalidad) y de la aprobación humana obligatoria**
- [ ] **Step 2: Ejecutar prueba y verificar que falla**
- [ ] **Step 3: Implementar `MatchingPsicologoService` en `ia_rules_engine.py`**
- [ ] **Step 4: Implementar vistas de generación, consulta y asignación confirmada por Coordinador en `clinica/views.py`**
- [ ] **Step 5: Ejecutar pruebas y verificar aprobación**

---

### Task 4: Servicio de Notificaciones Push FCM y Cola Transaccional (CU12 / HU-43)

**Files:**
- Create: `prototipo/backend/comunicacion/services.py` (o en `agenda/services.py`)
- Modify: `prototipo/backend/agenda/views.py`
- Modify: `prototipo/backend/agenda/urls.py`
- Create: `prototipo/backend/agenda/management/commands/despachar_recordatorios_push.py`
- Test: `prototipo/backend/tests/test_sprint3_fcm.py`

**Interfaces:**
- Consumes: `TokenFCM`, `NotificacionCita`, `Cita`
- Produces: `FCMNotificationService.enviar_push_paciente(paciente, titulo, cuerpo, payload) -> bool`
- Endpoint: `POST /api/v1/agenda/fcm-token/` (Registro de token del dispositivo móvil)

- [ ] **Step 1: Escribir pruebas para el enrolamiento de token FCM y despacho de recordatorios preventivos**
- [ ] **Step 2: Ejecutar pruebas y verificar que fallan**
- [ ] **Step 3: Implementar `FCMNotificationService` con manejo tolerante a fallos y registro de logs en `NotificacionCita`**
- [ ] **Step 4: Implementar endpoint de enrolamiento de token FCM y comando de despacho de recordatorios ($T-24\text{h}$ y $T-1\text{h}$)**
- [ ] **Step 5: Ejecutar pruebas y confirmar aprobación**

---

### Task 5: Lógica de Negocio de Agenda Móvil: Consulta, Cancelación Oportuna >24h y Bloqueo Tardío (CU11 / HU-41, HU-42)

**Files:**
- Modify: `prototipo/backend/agenda/views.py`
- Modify: `prototipo/backend/agenda/urls.py`
- Test: `prototipo/backend/tests/test_sprint3_cancellation_policy.py`

**Interfaces:**
- Consumes: Cita ID, fecha/hora programada, motivo de cancelación
- Produces:
  - `GET /api/v1/agenda/citas/mis-citas/` (Filtros: próximas e historial)
  - `POST /api/v1/agenda/citas/{id}/cancelar/` (Validación de ventana de 24h)

- [ ] **Step 1: Escribir pruebas unitarias que verifiquen cancelación exitosa con $\Delta t > 24\text{h}$ y HTTP 400 Bad Request con `CANCELLATION_WINDOW_EXPIRED` cuando $\Delta t \le 24\text{h}$**
- [ ] **Step 2: Ejecutar pruebas y verificar que fallan**
- [ ] **Step 3: Implementar la validación temporal estricta en `CitaViewSet.cancelar` en `agenda/views.py`**
- [ ] **Step 4: Ejecutar pruebas y verificar aprobación**

---

### Task 6: Teleconsulta WebRTC Móvil y Registro de Estado de Ánimo Diario (CU13, CU17 / HU-44, HU-45, HU-46)

**Files:**
- Modify: `prototipo/backend/agenda/views.py`
- Modify: `prototipo/backend/clinica/views.py`
- Modify: `prototipo/backend/clinica/urls.py`
- Test: `prototipo/backend/tests/test_sprint3_mood_teleconsulta.py`

**Interfaces:**
- Endpoints Teleconsulta:
  - `POST /api/v1/agenda/teleconsulta/{id}/unirse/` (Ventana 10 min antes - 45 min después)
  - `POST /api/v1/agenda/teleconsulta/{id}/finalizar/` (Registro de métricas y cierre)
- Endpoints Mood Tracker y Tareas:
  - `GET /api/v1/clinica/registro-animo/` y `POST /api/v1/clinica/registro-animo/` (Unicidad diaria por paciente)
  - `POST /api/v1/clinica/tareas/{id}/entregar/` (Entrega de tarea y bloqueo inmutable)

- [ ] **Step 1: Escribir pruebas para ventana de teleconsulta, entrega de tareas y registro diario de ánimo**
- [ ] **Step 2: Ejecutar pruebas y verificar que fallan**
- [ ] **Step 3: Implementar los endpoints en `agenda/views.py` y `clinica/views.py`**
- [ ] **Step 4: Ejecutar pruebas y verificar aprobación**

---

### Task 7: Integración y Conexión en la Aplicación Móvil Flutter (HU-40 a HU-46)

**Files:**
- Modify: `prototipo/movil/lib/services/agenda_service.dart`
- Modify: `prototipo/movil/lib/services/clinica_service.dart`
- Modify: `prototipo/movil/lib/screens/mis_citas_screen.dart`
- Modify: `prototipo/movil/lib/screens/dashboard_screen.dart`
- Modify: `prototipo/movil/lib/screens/mis_tareas_screen.dart`
- Test: `prototipo/movil/test/sprint3_mobile_flow_test.dart`

**Interfaces:**
- `AgendaService`: `getMisCitas()`, `cancelarCita(citaId, motivo)`
- `ClinicaService`: `getMisTareas()`, `entregarTarea(id, dificultad, notas)`, `registrarAnimo(estado, valor, factores, nota)`, `getHistorialAnimo()`

- [ ] **Step 1: Escribir prueba de widgets/unitarias en Flutter validando regla de 24h en interfaz y Mood Tracker**
- [ ] **Step 2: Ejecutar prueba y verificar comportamiento**
- [ ] **Step 3: Actualizar `agenda_service.dart` y `clinica_service.dart` con los endpoints de Sprint 3**
- [ ] **Step 4: Conectar `mis_citas_screen.dart` con la validación de ventana de 24 horas y diálogo de WhatsApp**
- [ ] **Step 5: Conectar `dashboard_screen.dart` con el Mood Tracker interactivo y persistencia**
- [ ] **Step 6: Ejecutar `flutter test` y confirmar que todos los tests pasan**

---

### Task 8: Consola Web de Triaje IA y Matching Asistido en Angular 17 (HU-47, HU-48)

**Files:**
- Modify/Create: `prototipo/web/src/app/core/services/triaje-ia.service.ts`
- Modify: `prototipo/web/src/app/modules/intake/ia-asistente-modal.component.ts`
- Create/Modify: `prototipo/web/src/app/modules/triaje/consola-triaje.component.ts` (o modal integrado)
- Test: `prototipo/web/tests/sprint3-triaje-matching.test.cjs`

**Interfaces:**
- `TriajeIAService`: `getAlertasCrisis()`, `getSugerenciasMatching(pacienteId)`, `asignarPsicologo(payload)`

- [ ] **Step 1: Escribir prueba en JavaScript/Node para el servicio de triaje y matching**
- [ ] **Step 2: Ejecutar prueba y verificar que falla**
- [ ] **Step 3: Implementar `triaje-ia.service.ts` con consumo de endpoints backend**
- [ ] **Step 4: Incorporar alerta visual de crisis y consola de recomendación Top 3 en Angular**
- [ ] **Step 5: Ejecutar prueba y verificar aprobación**

---

### Task 9: Suite de Integración y Verificación Integral Automatizada (`verify_sprint3.py`)

**Files:**
- Create: `prototipo/backend/verify_sprint3.py`
- Test: Ejecución completa en el entorno real PostgreSQL Multi-Tenant

**Interfaces:**
- Ejecuta los 13 casos de prueba canónicos de Sprint 3:
  - `CP-M01` / `CP-M02`: Autenticación móvil JWT y control de credenciales.
  - `CP-M03` / `CP-M04` / `CP-M05`: Consulta de citas, cancelación oportuna $>24\text{h}$ y bloqueo tardío $\le 24\text{h}$.
  - `CP-M06`: Registro de token FCM y despacho de recordatorio push.
  - `CP-M07`: Teleconsulta virtual WebRTC Jitsi Meet con control de ventana.
  - `CP-M08`: Entrega de tarea terapéutica inter-sesión e inmutabilidad.
  - `CP-M09`: Registro diario de estado de ánimo (Mood Tracker) con factores.
  - `CP-M10` / `CP-M11`: Clasificación asistida NLP de motivo y detección inmediata de crisis vital.
  - `CP-M12` / `CP-M13`: Matching multivariable Top 3 y validación humana obligatoria HITL.

- [ ] **Step 1: Diseñar y codificar `prototipo/backend/verify_sprint3.py` siguiendo la arquitectura de `verify_sprint2.py`**
- [ ] **Step 2: Ejecutar la suite completa sobre los tenants de prueba**
  Run: `prototipo\backend\venv\Scripts\python.exe prototipo/backend/verify_sprint3.py`
- [ ] **Step 3: Verificar que los 13 escenarios de prueba se ejecuten con éxito (100% Satisfactorio, 0 errores)**
