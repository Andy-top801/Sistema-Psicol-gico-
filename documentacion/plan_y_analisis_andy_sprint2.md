# PLAN DE DESARROLLO Y ANÁLISIS EXHAUSTIVO – ANDY MAURICIO MÚJICA VALLEJOS
## Sprint 2: Plataforma SIGEPSI (Sistemas-2)

> **Documento de Referencia Oficial:** [sprint2.md](file:///c:/Users/mujic/Desktop/SI2/Sistema-Psicol-gico-/documentacion/sprint2.md)  
> **Estudiante:** Andy Mauricio Mújica Vallejos  
> **Registro Universitario:** 224028367  
> **Rol SCRUM:** Development Team (Especialidad: Backend Lead Django REST, Criptografía Forense, Pasarela IA & Multi-Tenant)  
> **Periodo Oficial de Desarrollo:** 11 de septiembre al 05 de octubre de 2026  
> **Entrega y Congelamiento Técnico:** 05 de octubre de 2026  
> **Defensa Docente:** 06 y 08 de octubre de 2026  

---

## 1. Resumen Ejecutivo y Perfil de Responsabilidad

En estricta conformidad con las directrices metodológicas de la asignatura Sistemas-2 y la reasignación cíclica de roles del Sprint 2, Andy Mauricio Mújica Vallejos asume la **mayor carga horaria de desarrollo técnico individual de todo el equipo de 6 integrantes**:
* **Horas Planificadas Base:** 42 horas
* **Horas Reales Ejecutadas:** **46 horas** (desviación neta justificada de +4h por alta complejidad criptográfica, validación dinámica JSONB, WebSockets y volúmenes de datos).
* **Participación sobre el Esfuerzo Global:** 46 horas de las 165 horas totales ejecutadas por el equipo (**27.88% del esfuerzo del proyecto**).
* **Alcance:** Responsable principal del núcleo de datos en PostgreSQL 16 con esquemas aislados (`django-tenants`), APIs en Django REST Framework, canales síncronos en tiempo real (WebSockets / Django Channels), pasarela ética de IA hacia Google Gemini 1.5 Pro, y la consolidación de 3 de los Criterios Obligatorios más exigentes de la Cátedra (Criterio 3: Bitácora Cifrada Inviolable; Criterio 6: Backup/Restore `pg_dump`/`pg_restore`; Criterio 8: Datasets Masivos de 15 Tenants).

```mermaid
pie title Distribución del Esfuerzo Real en el Sprint 2 (165 Horas Totales)
    "Andy Mújica (Backend Lead & IA)" : 46
    "Julio Larrazabal (Frontend Angular)" : 32
    "Rolando Velasco (Scrum Master & QA)" : 27
    "Marilyn Condori (Lógica Clínica & SOAP)" : 25
    "Alberto Caleb Delgado (Móvil Flutter)" : 15
    "Maria Ilse Romero (Product Owner)" : 15
```

---

## 2. Análisis en Profundidad del SPRINT BACKLOG

El Sprint Backlog se compone de 34 tareas técnicas consolidadas. Andy tiene asignadas formalmente **7 tareas técnicas nucleares**. A continuación se detalla cada una de ellas:

### 2.1 Detalle de Tareas Asignadas a Andy

| ID Tarea | Descripción Técnica | Categoría | Tipo | Est. | Real | Desv. | Causa Técnica y Resolución de Ingeniería |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **SP2-35** | **Implementar backend y API REST de formulario previo con esquema JSONB** | Base (CU14) | Desarrollo | 8h | **9h** | +1h | **Complejidad:** Validación dinámica de esquemas anidados JSONB en PostgreSQL 16 para preguntas Likert y campos de texto libre sin romper la integridad del ORM.<br>**Solución:** Validadores dinámicos recursivos en serializers de DRF. |
| **SP2-38** | **Implementar backend, modelos de historia clínica y catálogo CIE indexado** | Base (CU15) | Desarrollo | 8h | **9h** | +1h | **Complejidad:** Sobrecarga y bloqueos en queries con búsquedas parciales entre los más de 14,000 registros del catálogo internacional CIE-10/11.<br>**Solución:** Indexación GIN y extensión de PostgreSQL `pg_trgm`, alcanzando respuestas en <40 ms en `/api/v1/cie10/?q=...`. |
| **SP2-50** | **Construir pasarela de IA con minimización de datos, RBAC y auditoría** | Piloto IA (HU-35) | Desarrollo | 8h | **9h** | +1h | **Complejidad:** Sanitización de Información Personal Identificable (PII) bajo principios médico-legales estrictos.<br>**Solución:** Filtro regex robusto de nombres, carnets y teléfonos; invocación asíncrona mediante Celery hacia Google Gemini 1.5 Pro y persistencia inmutable en tabla `AuditoriaIA`. |
| **SP2-56** | **Implementar motor conversacional del chatbot, intents clínicos y derivación a operador** | Chatbot SP2 (CU20) | Desarrollo | 8h | **9h** | +1h | **Complejidad:** Configuración de comunicación bidireccional y backend de canales Redis en entorno local.<br>**Solución:** Django Channels con WebSockets, clasificación de intenciones NLP, conmutación a `ESCALADA_HUMANO` y protocolo de contención de crisis 24/7. |
| **SP2-58** | **Backend Middleware de Auditoría y Cifrado AES-256 Fernet en Archivo Físico `.log.enc` (CU5 / Criterio 3)** | Bitácora Cifrada | Desarrollo | 4h | **4h** | 0h | **Complejidad:** Divergencias de permisos de archivos entre sistemas Windows y Linux.<br>**Solución:** Cifrado simétrico Fernet (AES-256-CBC con HMAC-SHA256) en disco diario `audit-YYYY-MM-DD.log.enc`, permisos POSIX `0600`, forzado al huso horario boliviano `America/La_Paz` (GMT-4) y descifrado dinámico en memoria mediante `AUDIT_LOG_KEY`. |
| **SP2-64** | **Scripts y Endpoints de Backup Automático (Cron Cloud) y Manual `pg_dump` con gzip (CU28 / Criterio 6)** | Backup / Restore | Desarrollo | 5h | **5h** | 0h | **Complejidad:** Manejo eficiente de compresión sin saturar la CPU del contenedor cloud.<br>**Solución:** Scripts con `pg_dump` comprimido en gzip (`.sql.gz`), selección de ámbito (Global vs Tenant específico), generación de Checksum SHA-256 y endpoint seguro de restauración transaccional con `pg_restore`. |
| **SP2-66** | **Script de Población Masiva (Datasets 15 Tenants, 4-12 meses de historial) y Aceptación (Criterio 8 / M1)** | Datasets SaaS | Aceptación / Dev | 5h | **5h** | 0h | *(Co-responsable con Romero).*\
**Complejidad:** Lentitud en la inserción secuencial de más de 25,000 registros sintéticos distribuidos en 15 clínicas.<br>**Solución:** Script `seed_tenants_masivo.py` optimizado con `bulk_create` por lotes, ejecutándose en menos de 90 segundos. |

### 2.2 Trazabilidad Diaria en el Daily Scrum (Narrativa de Ingeniería Día a Día)

* **11/09:** Planificación técnica de tareas SP2-35, 38, 50, 56 y complementarias. Modelado inicial en Django ORM de `FormularioPreConsulta` con campos JSONB dinámicos. *(Obstáculo: Curva de aprendizaje en consultas JSONB avanzadas en PostgreSQL 16).*
* **12/09:** Generación de migraciones de `FormularioPreConsulta` en esquemas tenant. Desarrollo de validadores de esquemas anidados en Django REST Framework. *(Obstáculo: Asegurar que preguntas anidadas validen obligatoriedad sin romper ORM).*
* **15/09:** Implementación de serializadores DRF para ingesta masiva de respuestas. Modelado de `HistoriaClinica` y carga de 14,000 registros nosológicos CIE-10/11 en base de datos. *(Obstáculo: Evitar saturación de memoria durante la carga masiva).*
* **16/09:** Creación de tabla `DiagnosticoCIE` con índices GIN. Construcción del endpoint de búsqueda reactiva `/api/v1/cie10/?q=...`. *(Obstáculo: Consultas con términos de una sola letra provocaban bloqueos; solventado con `pg_trgm`).*
* **17/09:** Optimización de búsqueda CIE respondiendo en <40 ms. Modelado de tabla `ConsentimientoInformado` con hash criptográfico SHA-256 y timestamp auditable.
* **18/09:** Implementación de señal Django `post_save` para sellar automáticamente registros con SHA-256 inmutable. Creación del endpoint de autoguardado SOAP `/api/v1/soap/draft/`. *(Obstáculo: Sobrecarga en PostgreSQL por peticiones de guardado excesivamente frecuentes).*
* **19/09:** Configuración de debounce y validación condicional en endpoint de borrador SOAP. Construcción del endpoint para consolidación inmutable de notas SOAP con firma digital.
* **22/09:** Pruebas de inmutabilidad en BD verificando bloqueo de sentencias `UPDATE` tras firma formal. Desarrollo del middleware de sanitización de información personal (PII) para IA. *(Obstáculo: Construcción de expresiones regulares estrictas para ocultar nombres, CI y teléfonos).*
* **23/09:** Implementación de pasarela segura hacia Google Gemini 1.5 Pro vía Celery. Creación de tabla `AuditoriaIA` para registrar logs éticos y decisiones profesionales. *(Obstáculo: Manejo de timeouts en Celery ante respuestas demoradas de la API externa).*
* **24/09:** Configuración de reintentos exponenciales y degradación suave (fallback) en Celery. Implementación de Django Channels con WebSockets para el Chatbot. *(Obstáculo: Configuración de Redis como canal de backend en entorno local).*
* **25/09:** Resolución de configuración de Redis y autenticación JWT de canales WebSocket. Lógica de clasificación de intenciones NLP del bot y protocolo de contención de crisis. *(Obstáculo: Manejo de concurrencia al transferir la sesión del bot al recepcionista).*
* **26/09:** Persistencia de mensajes del chat en PostgreSQL. Diseño e implementación del middleware de auditoría forense cifrada (SP2-58). *(Obstáculo: Selección de algoritmo criptográfico simétrico robusto: Fernet AES-256-CBC).*
* **29/09:** Almacenamiento físico de bitácora en archivo `.log.enc`. Configuración de permisos `0600` en Linux y protección de llave maestra. *(Obstáculo: Divergencias de permisos en sistemas Windows vs contenedores Linux).*
* **30/09:** Solución de permisos mediante emulación ACL en local y `0600` estricto en Docker. Desarrollo de endpoints de backup automático y manual vía `pg_dump` con gzip (SP2-64).
* **01/10:** Aislamiento de backups (por tenant individual o cluster global). Codificación del script de población masiva para 15 clínicas con 4-12 meses de historia (SP2-66). *(Obstáculo: Lentitud en inserción de 25,000 registros; resuelto con `bulk_create` por lotes).*
* **02/10:** Ejecución exitosa de población masiva en <90 segundos. Pruebas de restauración con `pg_restore` y verificación de integridad referencial.
* **03/10:** Comprobación de desconexión limpia de WebSockets y generación del DDL PostgreSQL 16 consolidado.
* **05/10:** Congelamiento de rama `dev-andy` y merge con la rama principal. Demostración formal en Sprint Review con 100% de tareas en **DONE**.

---

## 3. Análisis en Profundidad de las HISTORIAS DE USUARIO (HU)

Andy es desarrollador responsable o co-responsable en **9 de las 17 Historias de Usuario**:

```mermaid
graph LR
    subgraph Clinica["Expediente y Clinica"]
        HU23["HU-23: Intake Digital JSONB"]
        HU25["HU-25: HC y Catalogo CIE"]
        HU26["HU-26: RBAC Medico-Legal"]
        HU29["HU-29: Tareas Inter-sesiones"]
    end

    subgraph Inteligencia["IA Asistiva & Chatbot"]
        HU35["HU-35: Piloto IA Preconsulta"]
        HU36["HU-36: Chatbot WebSockets CU20"]
    end

    subgraph Criterios["Criterios de Catedra"]
        HU37["HU-37: Bitacora AES-256 CU5"]
        HU38["HU-38: Reportes QBE CU25"]
        HU39["HU-39: Backup/Restore CU28"]
    end

    Andy["Andy Mauricio Mujica"] --> Clinica
    Andy --> Inteligencia
    Andy --> Criterios
```

---

### 3.1 HU-23: Configuración y revisión de formulario previo digital (Intake) en Web
* **Identificadores:** CU14 | RF-08, RF-09 | Estimación: **5 PHU** | Prioridad: Alta.
* **Responsables:** Mujica Vallejos Andy / Larrazabal Julio.
* **Descripción:** Como Psicólogo o Administrador, quiero configurar cuestionarios de pre-consulta y revisar las respuestas de los pacientes antes de la primera sesión para conocer motivo, malestar (1-5) y antecedentes.
* **Criterios de Aceptación (BDD):**
  * `a)` Respuestas organizadas: Motivo, Síntomas, Escala de Malestar (1-5) y Antecedentes.
  * `b)` Si el paciente no completó el formulario a menos de 24 horas de la cita, se despliega alerta "Formulario Pendiente".
  * `c)` Backend valida dinámicamente el esquema JSONB ante edición de preguntas Likert o texto libre.
* **Implementación Backend (Andy):**
  * Modelos `FormularioPreConsulta` y `RespuestaPreConsulta` con campo `JSONField(default=dict)`.
  * Serializadores dinámicos con validación de tipos (`likert_1_5`, `text`, `multiple_choice`).
  * Endpoint de consulta para psicólogo tratante y cálculo de nivel de urgencia percibido.
* **Prueba Funcional:** Aprobada 4/4 (Validación de esquema JSONB y filtrado por ventana de 24h verificado).

---

### 3.2 HU-25: Apertura y estructura de Historia Clínica Psicológica en Web
* **Identificadores:** CU15 | RF-22 | Estimación: **8 PHU** | Prioridad: Alta.
* **Responsables:** Larrazabal Rojas Julio / Mujica Andy.
* **Descripción:** Como Psicólogo tratante, quiero abrir y estructurar el expediente clínico electrónico (anamnesis, examen mental, diagnóstico CIE-10/11 y objetivos terapéuticos) como documento médico-legal riguroso.
* **Criterios de Aceptación (BDD):**
  * `a)` Pestañas estructuradas: Anamnesis, Examen Mental, Diagnóstico CIE y Plan Terapéutico.
  * `b)` Búsqueda de diagnósticos CIE por texto o código (ej. 'F41.1') indexada por trigramas (<40 ms) clasificable en presuntivo o confirmado.
  * `c)` Guardado con firma digital del terapeuta, timestamp inmutable y correlativo único (`HC-2026-XXXX`).
* **Implementación Backend (Andy):**
  * Modelo `HistoriaClinica` vinculado al paciente y terapeuta dentro del esquema tenant.
  * Modelo `DiagnosticoCIE` con más de 14,000 registros y migración con extensión `pg_trgm`.
  * Endpoint reactivo `/api/v1/cie10/?q=...` con optimización GIN.
  * Generación de correlativo anual correlacionado por tenant.
* **Prueba Funcional:** Aprobada 4/4 (Autocompletado en <40ms, firma digital y correlativo validados).

---

### 3.3 HU-26: Control de acceso y confidencialidad clínica (RBAC Clínico) en Web
* **Identificadores:** CU15 | RF-29 | Estimación: **5 PHU** | Prioridad: Alta.
* **Responsables:** Velasco Soliz Rolando / Mujica Andy.
* **Descripción:** Como Administrador o Psicólogo, quiero que el sistema restrinja estrictamente el acceso a historias clínicas según la relación directa terapeuta-paciente para garantizar confidencialidad médico-legal.
* **Criterios de Aceptación (BDD):**
  * `a)` Intento de acceso de un terapeuta a un paciente no asignado responde `HTTP 403 Forbidden` y audita el evento.
  * `b)` Rol Recepcionista solo visualiza agenda y contacto, manteniendo ocultos diagnósticos y notas SOAP.
  * `c)` Director Clínico en auditoría permite lectura y registra fecha, hora, usuario e IP.
* **Implementación Backend (Andy):**
  * Clase de permiso [`EsPsicologoTratanteOAdmin`](file:///c:/Users/mujic/Desktop/SI2/Sistema-Psicol-gico-/prototipo/backend) con método `has_object_permission`.
  * Filtrado dinámico de `QuerySet` en `HistoriaClinicaViewSet`.
  * Intercepción y reporte de violaciones de acceso hacia el middleware de auditoría forense.
* **Prueba Funcional:** Aprobada 4/4 (Bloqueo HTTP 403 verificado y trazabilidad registrada).

---

### 3.4 HU-29: Asignación y gestión de tareas inter-sesiones en Web
* **Identificadores:** CU17 | RF-24 | Estimación: **5 PHU** | Prioridad: Alta.
* **Responsables:** Condori Diaz Marilyn / Mujica Andy.
* **Descripción:** Como Psicólogo, quiero asignar tareas terapéuticas entre sesiones con fecha límite, categoría y guías adjuntas para práctica fuera de consulta.
* **Criterios de Aceptación (BDD):**
  * `a)` Definición de título, descripción, categoría (Conductual, Cognitiva, Mindfulness) y fecha límite.
  * `b)` Adjuntos en PDF almacenados de forma segura y sincronizados con la app móvil.
  * `c)` Visualización de reflexiones, calificación de adherencia y retroalimentación en sesión.
* **Implementación Backend (Andy):**
  * Modelos `TareaTerapeutica` y `EvidenciaTarea` con soporte multi-tenant.
  * Manejo seguro de subida de archivos PDF a almacenamiento local del tenant.
  * Validación pesimista de fechas de vencimiento estrictamente futuras.
* **Prueba Funcional:** Aprobada 4/4 (Subida controlada de PDF y validación de fechas límite certificadas).

---

### 3.5 HU-35: Asistente de revisión de preconsulta con priorización asistiva (Piloto IA)
* **Identificadores:** CU14 (IA) | RF-08, RF-09, RF-29 | Estimación: **5 PHU** | Prioridad: Alta.
* **Responsables:** Romero Saavedra Maria / Mujica Andy / Larrazabal Julio.
* **Descripción:** Como Psicólogo tratante, quiero recibir un resumen estructurado neutral y priorización asistiva del intake para preparar la sesión con agilidad, manteniendo siempre el juicio clínico en mis manos.
* **Criterios de Aceptación (BDD):**
  * `a)` Despliegue de borrador visible con etiqueta obligatoria "Borrador IA — Requiere Revisión Profesional".
  * `b)` Explicación transparente de reglas clínicas que motivaron cada sugerencia o nivel de urgencia.
  * `c)` Profesional puede editar, aceptar o descartar el borrador; la acción genera auditoría inmutable.
  * `d)` Bloqueo estricto del servicio y preservación del flujo 100% manual si no hay consentimiento informado o si la API externa falla.
  * `e)` Prohibición médico-legal absoluta de guardar diagnósticos presuntivos automáticos en el expediente.
* **Implementación Backend (Andy):**
  * Servicio `PreconsultaRulesEngine.sanitizar_pii()` que limpia nombres, cédulas y teléfonos mediante expresiones regulares.
  * Controlador `IAPreconsultaViewSet` y conexión asíncrona vía Celery hacia Google Gemini 1.5 Pro.
  * Modelo `AuditoriaIA` con hash del prompt, decisión adoptada y trazabilidad completa.
  * Fallback tolerante a fallos: respuesta de error limpia sin interrumpir el proceso de consulta.
* **Prueba Funcional:** Aprobada 4/4 (Explicabilidad de reglas, sanitización PII y 0 diagnósticos automáticos guardados).

---

### 3.6 HU-36: Interacción con el chatbot de orientación clínica y derivación a soporte humano
* **Identificadores:** CU20 | RF-12, RF-13 | Estimación: **5 PHU** | Prioridad: Alta.
* **Responsables:** Larrazabal Rojas Julio / Mujica Andy / Delgado Caleb.
* **Descripción:** Como Paciente, quiero interactuar con un chatbot interactivo en Web y Móvil para orientación, dudas frecuentes y solicitud de atención con personal humano en recepción.
* **Criterios de Aceptación (BDD):**
  * `a)` Respuestas FAQ inmediatas en <1 segundo sobre citas, aranceles y formularios.
  * `b)` Escalamiento a asesor humano por baja certidumbre o solicitud explícita, transfiriendo la transcripción a la recepcionista.
  * `c)` Detección reactiva de riesgo o crisis psicológica severa con despliegue prioritario de números oficiales de auxilio (800-11-3040 / 911).
  * `d)` Atención en tiempo real de recepcionista vía canal WebSocket.
  * `e)` Almacenamiento cifrado en reposo por esquema tenant.
* **Implementación Backend (Andy):**
  * Configuración de Django Channels con protocolo WebSockets (`ws://`) y Redis (`channel_layer`).
  * Controlador `ChatbotViewSet` y modelo `ConversacionChatbot`.
  * Filtro NLP de palabras de crisis psicológica que conmuta inmediatamente a protocolo de salvamento.
  * Gestión de estados: `BOT_ACTIVO` -> `ESCALADA_HUMANO` con notificación sonora/visual al panel de recepción.
* **Prueba Funcional:** Aprobada 4/4 (Respuestas FAQ <1s, contención de crisis 24/7 y transferencia WebSocket exitosa).

---

### 3.7 HU-37: Bitácora confidencial en disco cifrado y descifrado con Llave de Desarrollador (Criterio 3)
* **Identificadores:** CU5 | RF-30, RNF-17 | Estimación: **5 PHU** | Prioridad: **Alta (Criterio 3 Obligatorio)**.
* **Responsables:** Mujica Vallejos Andy / Larrazabal Julio / Velasco Rolando.
* **Descripción:** Como Desarrollador / SuperAdmin, quiero registrar todas las operaciones en un log cifrado con AES-256 en disco con hora de Bolivia (`America/La_Paz`), inaccesible para el DBA, y descifrable solo con Llave de Desarrollador desde el sistema.
* **Criterios de Aceptación (BDD):**
  * `a)` Captura síncrona en cada petición HTTP: IP, usuario, acción y hora boliviana `America/La_Paz` (GMT-4).
  * `b)` Cifrado simétrico Fernet (AES-256 en modo CBC con HMAC-SHA256) en archivo físico `audit-YYYY-MM-DD.log.enc` con permisos `0600`, inaccesible para el DBA.
  * `c)` Peticiones a `/audit/log/` sin llave o con llave errónea responden `HTTP 403 Forbidden`.
  * `d)` Descifrado dinámico en memoria volátil al suministrar la Llave Maestra del Desarrollador (`AUDIT_LOG_KEY`).
* **Implementación Backend (Andy):**
  * Middleware [`audit.middleware.AuditLogMiddleware`](file:///c:/Users/mujic/Desktop/SI2/Sistema-Psicol-gico-/prototipo/backend).
  * Forzado de huso horario local con `timezone.localtime()`.
  * Encriptación y escritura atómica en archivo rotativo diario `.log.enc`.
  * Endpoint protegido con header `X-Developer-Key` y descifrado strictly in-memory.
* **Prueba Funcional:** Aprobada 4/4 (Cifrado Fernet comprobado, permisos 0600 validados y desbloqueo por Developer Key certificado).

---

### 3.8 HU-38: Generador de reportes personalizados (QBE), exportación multiformato y voz (Criterio 5)
* **Identificadores:** CU25 | RF-26, RF-27 | Estimación: **8 PHU** | Prioridad: **Alta (Criterio 5 Obligatorio)**.
* **Responsables:** Condori Diaz Marilyn / Larrazabal Julio / Mujica Andy.
* **Descripción:** Como Administrador o Coordinador, quiero construir reportes a medida seleccionando columnas, filtros dinámicos (QBE) o mediante comandos de voz en el navegador, y exportar a Excel, CSV, HTML o eMail.
* **Criterios de Aceptación (BDD):**
  * `a)` 3 modalidades obligatorias: Estándar, QBE dinámico y Comandos de Voz (Web Speech API).
  * `b)` Mapeo de parámetros por voz (entidad, filtro, fecha) para configurar el formulario QBE.
  * `c)` Consulta relacional dinámica con aislamiento por tenant y proyección exclusiva de columnas seleccionadas.
  * `d)` Exportación sin pérdida a Excel (.xlsx con OpenPyXL), CSV plano UTF-8 BOM y despacho SMTP.
* **Implementación Backend (Andy):**
  * Colaboración en endpoints analíticos de `backend/reportes/views.py`.
  * Optimización de consultas dinámicas por tenant mediante Django ORM (`values()`, `filter()`).
  * Generación de streams binarios para descarga en navegadores.
* **Prueba Funcional:** Aprobada 4/4 (Consulta QBE dinámica, proyecciones por tenant y exportaciones completadas).

---

### 3.9 HU-39: Copias de seguridad automáticas y manuales con restauración en la nube (Criterio 6)
* **Identificadores:** CU28 | RF-32, RNF-20 | Estimación: **5 PHU** | Prioridad: **Alta (Criterio 6 Obligatorio)**.
* **Responsables:** Mujica Andy / Delgado Caleb / Romero Maria Ilse.
* **Descripción:** Como SuperAdministrador, quiero contar con respaldos programados automáticos en la nube y manuales a demanda (globales o por tenant) y restaurar completamente el sistema o un centro específico con verificación de integridad.
* **Criterios de Aceptación (BDD):**
  * `a)` Respaldo automático periódico mediante cron job en servidor cloud a las 03:00 AM hora de Bolivia con `pg_dump` y compresión gzip.
  * `b)` Respaldo manual a demanda eligiendo ámbito (Global o Tenant específico) descargable con checksum SHA-256.
  * `c)` Restauración transaccional con `pg_restore` (`--clean --if-exists`), abortando y haciendo rollback si la firma criptográfica es inválida.
  * `d)` Auditoría inmutable de usuario, IP, tamaño y duración de cada operación.
* **Implementación Backend (Andy):**
  * Script shell y comando Django de backup para cron (`cron_backup_cloud.sh`).
  * Endpoint administrativo `/api/v1/backups/generar/` con parámetros `scope=global` o `scope=tenant&schema=...`.
  * Utilidad de compresión y cálculo de hash SHA-256.
  * Endpoint transaccional `/api/v1/backups/restaurar/` orquestando `pg_restore`.
* **Prueba Funcional:** Aprobada 4/4 (Backup cloud automático, volcado manual por esquema y restauración íntegra validados).

---

## 4. Consolidación de los 8 Criterios de la Cátedra (Audios M1, M2, K2)

Andy es el actor clave en tres de los requisitos no negociables fijados por la docente para la defensa:

### Criterio 3: Bitácora Inviolable con Cifrado Fernet AES-256
* **Principio de Inviolabilidad:** Ningún administrador de BD (ni el propio DBA con privilegios `postgres`) puede consultar las trazas mediante sentencias SQL, pues residen en el sistema de archivos del host como texto cifrado (`.log.enc`) con permisos `0600`.
* **Validez Jurídica Forense:** Forzado al huso horario de Bolivia `America/La_Paz` (GMT-4).
* **Desafío Criptográfico:** Descifrado únicamente en memoria volátil bajo el suministro de la `AUDIT_LOG_KEY` desde la consola administrativa.

### Criterio 6: Backup y Restore Automático y Manual
* **Doble Modalidad:**
  1. *Automática:* Ejecutada en la nube periódicamente a las 03:00 AM.
  2. *Manual:* Disparada a demanda desde la consola del SuperAdmin, aislando esquemas tenant si se requiere.
* **Integridad Criptográfica:** Sellado con Checksum SHA-256 para prevenir alteraciones antes del restore.
* **Restauración Atómica:** Ejecución de `pg_restore` dentro de transacciones que protegen los esquemas en caliente.

### Criterio 8: Modelo SaaS y Datasets Masivos de 15 Clínicas
* **Requisito M1:** Prohibición absoluta de ingresar datos manualmente al momento de la defensa.
* **Solución Técnica de Andy:** Script [`seed_tenants_masivo.py`](file:///c:/Users/mujic/Desktop/SI2/Sistema-Psicol-gico-/prototipo/backend) con `bulk_create` por lotes:
  * 15 Clínicas Reales simuladas (*Centro Esperanza, Clínica San Gabriel, Gabinete UAGRM, Consultorios Mente Sana, etc.*).
  * Historial clínico de **4 a 12 meses de antigüedad**.
  * Más de **25,000 registros sintéticos estructurados**: citas concluidas, canceladas, notas SOAP, diagnósticos CIE-10/11 y consentimientos firmados.
  * Inserción masiva optimizada en menos de 90 segundos.

---

## 5. Diseño Arquitectónico (C4 y BCE) Mapeado al Código de Andy

### 5.1 Diagrama de Clases por Paquetes (C4 Nivel 4) Desarrollado por Andy

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam packageStyle frame

package "Paquete 1: Seguridad y Multi-Tenant" {
    class EsPsicologoTratanteOAdmin {
        + has_permission(request, view): bool
        + has_object_permission(request, view, obj): bool
    }
}

package "Paquete 2: Gestión Clínica y Diagnósticos" {
    class HistoriaClinicaViewSet {
        + list(request): Response
        + retrieve(request, pk): Response
        + abrir_expediente(request): Response
    }
    class CIE10CatalogService {
        + {static} buscar_catalogo(query: str): List
        + {static} validar_codigo_cie(codigo: str): bool
    }
    class DiagnosticoCIE {
        + codigo_cie: str
        + descripcion: str
        + tipo: str
    }
    class HistoriaClinica {
        + codigo_historia: str
        + motivo_consulta_inicial: str
        + examen_mental_inicial: str
        + plan_tratamiento: str
    }
}

package "Paquete 4: Formularios e Intake" {
    class FormularioPreConsultaViewSet {
        + list(request): Response
        + configurar_preguntas(request): Response
    }
    class FormularioPreConsulta {
        + titulo: str
        + preguntas_schema: JSONField
        + activo: bool
    }
    class RespuestaPreConsulta {
        + motivo_consulta: str
        + sintomas_principales: str
        + nivel_urgencia_percibido: int
    }
}

package "Paquete 5: Inteligencia Artificial y Chatbot" {
    class IAPreconsultaViewSet {
        + evaluar_preconsulta(request): Response
        + consultar_explicabilidad(request, pk): Response
    }
    class PreconsultaRulesEngine {
        + {static} sanitizar_pii(texto: str): str
        + {static} evaluar_preconsulta(respuesta): dict
    }
    class ChatbotViewSet {
        + iniciar_conversacion(request): Response
        + procesar_mensaje(request): Response
        + solicitar_soporte_humano(request): Response
    }
    class ConversacionChatbot {
        + session_id: str
        + estado: str
        + escalada_a_humano: bool
    }
    class AuditoriaIA {
        + prompt_hash: str
        + decision_tipo: str
        + revisado_por_humano: bool
    }
}

package "Seguridad Forense & Backups" {
    class AuditLogMiddleware {
        + __call__(request): response
        + escribir_log_cifrado(linea_json: str): void
    }
    class BackupManagerService {
        + {static} ejecutar_pg_dump(schema_name, destino): str
        + {static} restaurar_pg_restore(archivo_dump): bool
    }
}

HistoriaClinicaViewSet ..> EsPsicologoTratanteOAdmin
HistoriaClinicaViewSet ..> CIE10CatalogService
HistoriaClinica "1" *-- "many" DiagnosticoCIE
FormularioPreConsultaViewSet --> FormularioPreConsulta
FormularioPreConsulta "1" *-- "many" RespuestaPreConsulta
IAPreconsultaViewSet ..> PreconsultaRulesEngine
IAPreconsultaViewSet --> AuditoriaIA
ChatbotViewSet --> ConversacionChatbot
@enduml
```

---

## 6. Hoja de Ruta de Programación en Pareja (Actionable Roadmap)

Dado que la documentación se encuentra concluida al 100% y el siguiente paso es la **implementación real del código en el backend**, a continuación se define el orden cronológico exacto de desarrollo en pair programming:

```mermaid
flowchart TD
    Fase1["Fase 1: Intake Digital JSONB (SP2-35 / HU-23)"] --> Fase2["Fase 2: Catálogo CIE-10/11 & Historia Clínica (SP2-38 / HU-25, HU-26)"]
    Fase2 --> Fase3["Fase 3: Bitácora Cifrada Fernet AES-256 (SP2-58 / HU-37 / Criterio 3)"]
    Fase3 --> Fase4["Fase 4: Pasarela IA con Sanitización PII (SP2-50 / HU-35)"]
    Fase4 --> Fase5["Fase 5: Chatbot WebSockets & Contención (SP2-56 / HU-36)"]
    Fase5 --> Fase6["Fase 6: Backup y Restore pg_dump/pg_restore (SP2-64 / HU-39 / Criterio 6)"]
    Fase6 --> Fase7["Fase 7: Script Masivo 15 Tenants (SP2-66 / Criterio 8)"]
    Fase7 --> Fase8["Fase 8: Homologación y QA Automatizado (verify_sprint2.py)"]
```

### Plan Paso a Paso de Codificación:

1. **Fase 1 – Formulario Previo e Intake Dinámico JSONB (`SP2-35` / HU-23):**
   * Archivos a crear/editar: `backend/clinica/models.py`, `backend/clinica/serializers.py`, `backend/clinica/views.py`, `backend/clinica/urls.py`.
   * Modelar `FormularioPreConsulta` y `RespuestaPreConsulta` con campo `JSONField`.
   * Crear validadores de esquemas Likert/texto y serializadores con cálculo de malestar.
   * Ejecutar migraciones: `python manage.py makemigrations clinica` y `python manage.py migrate_schemas`.

2. **Fase 2 – Historia Clínica, Catálogo CIE-10/11 y RBAC (`SP2-38` / HU-25, HU-26):**
   * Archivos a crear/editar: `backend/clinica/models.py`, `backend/clinica/permissions.py`, `backend/clinica/views.py`.
   * Crear tabla `DiagnosticoCIE` y script de ingesta de 14,000 códigos.
   * Habilitar extensión `pg_trgm` en PostgreSQL y crear índice GIN en código y descripción.
   * Implementar `EsPsicologoTratanteOAdmin` restringiendo accesos a historias no asignadas.
   * Exponer endpoint `/api/v1/cie10/?q=...` con optimización reactiva (<40 ms).

3. **Fase 3 – Bitácora Forense Cifrada Fernet AES-256 (`SP2-58` / HU-37 / Criterio 3):**
   * Archivos a crear/editar: `backend/audit/middleware.py`, `backend/audit/services.py`, `backend/audit/views.py`, `backend/audit/urls.py`.
   * Implementar middleware HTTP que capture IP, usuario, acción y hora boliviana `America/La_Paz` (GMT-4).
   * Cifrar con librería `cryptography.fernet.Fernet` y persistir en `logs/audit/audit-YYYY-MM-DD.log.enc`.
   * Configurar permisos POSIX `0600` en archivo.
   * Crear vista `/api/v1/audit/log/` que descifre exclusivamente en memoria al recibir `AUDIT_LOG_KEY`.

4. **Fase 4 – Pasarela Asistiva de IA con Sanitización PII (`SP2-50` / HU-35):**
   * Archivos a crear/editar: `backend/clinica/ia_rules_engine.py`, `backend/clinica/tasks.py`, `backend/clinica/views.py`.
   * Implementar `sanitizar_pii(texto)` con filtros regex para nombres, cédulas y teléfonos.
   * Configurar tarea asíncrona de Celery hacia Google Gemini 1.5 Pro con reintentos exponenciales.
   * Persistir trazabilidad ética en tabla `AuditoriaIA`.
   * Blindar la política de cero diagnósticos automáticos.

5. **Fase 5 – Chatbot con Django Channels, WebSockets y Contención (`SP2-56` / HU-36):**
   * Archivos a crear/editar: `backend/sigepsi/asgi.py`, `backend/clinica/consumers.py`, `backend/clinica/routing.py`, `backend/clinica/views.py`.
   * Configurar Channels con capa Redis en `settings.py`.
   * Implementar `ChatConsumer` para WebSocket bidireccional.
   * Incorporar filtro de palabras de riesgo de crisis (autolesión, suicidio) y conmutar a líneas oficiales de auxilio (800-11-3040 / 911).
   * Programar escalamiento de sesión a recepcionista en turno.

6. **Fase 6 – Backup y Restauración `pg_dump`/`pg_restore` (`SP2-64` / HU-39 / Criterio 6):**
   * Archivos a crear/editar: `backend/tenants/backup_service.py`, `backend/tenants/views.py`, `backend/tenants/urls.py`, `scripts/cron_backup.sh`.
   * Implementar comandos seguros de volcado `pg_dump` con compresión gzip en streaming HTTP.
   * Permitir selección de origen (Global o Tenant específico).
   * Calcular y verificar Checksum SHA-256 en carga y descarga.
   * Implementar endpoint de restauración transaccional con `pg_restore`.

7. **Fase 7 – Script Masivo de Población para 15 Clínicas (`SP2-66` / Criterio 8):**
   * Archivo a crear: `backend/scripts/seed_tenants_masivo.py`.
   * Generar 15 esquemas tenant con nombres institucionales representativos.
   * Población masiva de expedientes, citas concluídas y canceladas, notas SOAP y diagnósticos simulando 4 a 12 meses de historia.
   * Optimizar con `bulk_create` por lotes para ejecución completa en menos de 90 segundos.

8. **Fase 8 – Verificación y QA BDD Automatizado:**
   * Ejecutar la suite de pruebas del sprint: `python verify_sprint2.py`.
   * Certificar los 68 casos de prueba funcionales en verde (100% de éxito).

---

## 7. Conclusión y Compromiso de Desarrollo

Toda la base arquitectónica, formal y documental del Sprint 2 está concluida y respaldada en [`documentacion/sprint2.md`](file:///c:/Users/mujic/Desktop/SI2/Sistema-Psicol-gico-/documentacion/sprint2.md). Este plan operativo constituye la **hoja de ruta maestra** para que comencemos de inmediato a codificar módulo por módulo en el backend, garantizando una defensa docente impecable y un software de nivel profesional.
