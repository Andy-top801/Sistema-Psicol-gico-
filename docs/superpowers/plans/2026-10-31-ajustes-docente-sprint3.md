# Ajustes Metodológicos y Técnicos del Sprint 3 (Observaciones de la Cátedra) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Actualizar y enriquecer integralmente la memoria técnica del Sprint 3 (`documentacion/sprint3.md`) para subsanar el 100% de las observaciones, críticas metodológicas y exigencias evaluativas dictadas por la docente evaluadora en las sesiones de revisión de proyectos.

**Architecture:** Se aplica una estrategia de refactorización y enriquecimiento documental estructurado sobre `documentacion/sprint3.md`. Se integran componentes visuales (URL y Código QR de producción), se sintetiza el Objetivo del Sprint bajo el estándar conciso exigido, se amplía la arquitectura lógica a 4 capas canónicas (incorporando Software de Sistema), se reajusta el diagrama de despliegue con multiplicidad y contenedores Docker, se incorpora la Bitácora de auditoría en los diagramas de secuencia, se formaliza la trazabilidad entre Sprints en la Revisión, se recalibran las horas estimadas vs. reales eliminando desvíos artificiales de cero horas, y se documenta la suite de reportes de salida en PDF/HTML.

**Tech Stack:** Markdown, PlantUML 2.5+, UML 2.5 (BCE: Boundary-Control-Entity, Deployment, Packages, Sequence), Scrum Framework, Django REST Framework, Flutter 3.x, PostgreSQL 16 Multi-Tenant, Docker.

**Spec:** [Cambios_Y_Observaciones_Docente_Sprint3.md](file:///c:/Users/User/Documents/2-2026/SI2\PROYECTO_GRUPAL_OFI\datos\Cambios_Y_Observaciones_Docente_Sprint3.md)

## Global Constraints

- **Ponderación:** 50% documento / 50% implementación. Todo modelo debe coincidir biunívocamente con el código y base de datos.
- **Congelamiento de código y entrega:** Domingo 02 de noviembre de 2026 a las 23:59.
- **Formato de Objetivos:** Corto, singular, claro y categórico (cumplimiento del 100%).
- **Arquitectura Lógica:** 4 capas formales: Presentación, Negocio/Backend, Datos y Software de Sistema.
- **Arquitectura Física:** Diagrama de despliegue con nombres exactos de servidores, multiplicidad (`1..*`), contenedores Docker y notas UML explicativas.
- **Secuencia BCE:** Prohibido el diálogo entre entidades. Controladores orquestan con mensajes a entidades. Presencia obligatoria de la Bitácora en transacciones exitosas.
- **Scrum:** Tabla diaria con tarea y avance explícito. Horas reales distintas de estimadas con justificación de variación real.

## Review Focus

1. **Multiplicidad en nodos de despliegue:** Los nodos de clientes (Workstation y Smartphone) deben tener `1..*` explícito para que no parezca un único cliente conectado a la nube.
2. **Capa 4 (Software de Sistema):** Debe existir y corresponder exactamente con los servidores y servicios declarados en el Diagrama de Despliegue.
3. **Presencia de Bitácora en Secuencias:** Cada diagrama de secuencia debe mostrar la entidad de Bitácora registrando la auditoría al completarse la operación.
4. **Variación realista de horas:** Las horas estimadas y reales en 7.7.1 no pueden tener cero variación en todas las tareas; deben reflejar la variabilidad del Daily Scrum.
5. **URL y Código QR:** Deben figurar en la portada para garantizar la verificación rápida por parte de la docente.

---

### Task 1: Portada Oficial y Sección de Acceso Evaluativo (URL de Producción + Código QR)

**Files:**
- Modify: `documentacion/sprint3.md:1-25`

**Interfaces:**
- Consumes: Dominio público de producción de SIGEPSI (`https://sigepsi.online`), esquemas tenant y credenciales de evaluación.
- Produces: Sección destacada en la cabecera del documento con enlace HTTPS directo y artefacto visual de Código QR (renderizado en ASCII / imagen) para validación docente inmediata.

- [x] **Step 1: Verificar la cabecera actual del documento `documentacion/sprint3.md`**
  Inspeccionar líneas 1 a 20 de `documentacion/sprint3.md` para ubicar el bloque de metadatos del Sprint 3.

- [x] **Step 2: Redactar e insertar el bloque de Evaluación y Acceso en Producción**
  Insertar inmediatamente después de los metadatos iniciales un cuadro destacado con:
  - URL oficial del entorno de producción (`https://sigepsi.online`).
  - Subdominio de evaluación tenant (`https://clinica-san-martin.sigepsi.online`).
  - Código QR de acceso directo para escaneo con smartphone.
  - Credenciales de prueba rápida para roles Evaluador / Coordinador / Paciente.

- [x] **Step 3: Verificar visualización y renderizado del bloque en Markdown**
  Comprobar que los enlaces `file://` y `https://` y el diagrama de bloque QR mantengan la estética profesional.

---

### Task 2: Reestructuración y Síntesis del Objetivo del Sprint 3 (Sección 7.1.1)

**Files:**
- Modify: `documentacion/sprint3.md:98-125`

**Interfaces:**
- Consumes: Sección `Cambios_Y_Observaciones_Docente_Sprint3.md` (Punto 2.2: *"el objetivo siempre es uno solo... normalmente siempre son cortitos... pero el cumplimiento debe ser del 100%"*).
- Produces: Redacción singular `7.1.1 Objetivo del Sprint 3` de máximo 2 oraciones, trasladando el desglose de características a la subsección `Alcance Funcional del Incremento Entregable`.

- [x] **Step 1: Leer la sección actual 7.1.1 en `documentacion/sprint3.md`**
  Revisar líneas 98 a 110 donde actualmente figura un encabezado en plural *"Objetivos del Sprint 3"* y una lista numerada de 7 puntos.

- [x] **Step 2: Modificar el encabezado a singular y redactar el Objetivo único y conciso**
  Reemplazar el texto por:
  ```markdown
  ### 7.1.1 Objetivo del Sprint 3
  
  Consolidar de forma integral la interacción ubicua del paciente mediante el despliegue productivo de la aplicación móvil nativa (Flutter 3.x) y automatizar el triaje clínico asistido con algoritmos multivariables de Inteligencia Artificial supervisados bajo el principio de validación médica obligatoria (*Human-in-the-Loop*), garantizando el 100% de cumplimiento funcional sobre los casos de uso CU12, CU21 y CU22 en la arquitectura SaaS multi-inquilino.
  ```

- [x] **Step 3: Reubicar el listado detallado bajo una subsección subordinada**
  Colocar el detalle de tareas técnicas bajo el título `#### Alcance Operativo del Incremento Entregable`, asegurando que no se confunda con el objetivo general del ciclo.

---

### Task 3: Arquitectura en 4 Capas con Capa de Software de Sistema (Sección 7.2.1.1.1)

**Files:**
- Modify: `documentacion/sprint3.md:950-1045`

**Interfaces:**
- Consumes: Directriz docente (`CambiosProyecto1.md`, Línea 107: *"esta última capa que se llama software de sistema, esta es software de sistema, por favor"*).
- Produces: Texto explicativo y diagrama PlantUML de Arquitectura Lógica en 4 Capas: Presentación, Lógica de Negocio, Datos y Software de Sistema.

- [x] **Step 1: Revisar la sección 7.2.1.1.1 actual**
  Verificar que el modelo actual solo declara 3 capas (`Capa1: Presentación`, `Capa2: Lógica de Negocio`, `Capa3: Datos`).

- [x] **Step 2: Agregar la Capa 4 (Software de Sistema) en el texto descriptivo**
  Detallar los componentes de la capa base:
  - Sistema Operativo: Ubuntu 22.04 LTS Kernel 5.15.
  - Motor de Contenedores: Docker Engine 25.x & Docker Compose v2.
  - Servidor Web y Proxy Inverso: Nginx 1.24 con terminación TLS 1.3.
  - Motor SGBD: PostgreSQL 16.2 RDBMS daemon.
  - Planificador y Daemon de Procesos: Systemd & Redis 7.2 Broker.

- [x] **Step 3: Actualizar el código PlantUML del Diagrama de Capas**
  Incorporar en el bloque PlantUML (líneas 982-1041):
  ```plantuml
  package "«layer»\nCapa 4: Software de Sistema (Infraestructura y Servicios Base)" as Capa4 {
    [Sistema Operativo Host\n[Ubuntu 22.04 LTS / Linux Kernel 5.15]] as OS
    [Motor de Contenedores\n[Docker Engine 25.x & Containerd]] as Docker
    [Proxy Inverso & Gateway\n[Nginx 1.24 SSL / HTTP/2]] as NginxSys
    [Gestor de Procesos y Broker\n[Redis 7.2 & Celery Daemon]] as BrokerSys
  }
  Capa3 ..> Capa4 : se ejecuta sobre
  Capa2 ..> Capa4 : gestionado por
  ```

- [x] **Step 4: Validar la consistencia entre Software de Sistema y el Diagrama de Despliegue**
  Comprobar que los nombres y versiones coincidan exactamente con la sección 7.2.1.1.3.

---

### Task 4: Enriquecimiento del Diagrama de Despliegue UML (Sección 7.2.1.1.3)

**Files:**
- Modify: `documentacion/sprint3.md:1140-1250`

**Interfaces:**
- Consumes: Criterios docentes de despliegue (`CambiosProyecto1.md`, Líneas 71-85: multiplicidad `1..*`, contenedor Docker, nombre explícito del servidor y notas UML explicativas).
- Produces: Diagrama de despliegue PlantUML actualizado y enriquecido con topología completa, multiplicidades y notas explicativas vinculadas con dependencias.

- [x] **Step 1: Inspeccionar el diagrama PlantUML de despliegue actual**
  Revisar líneas 1160 a 1249 de `documentacion/sprint3.md`.

- [x] **Step 2: Actualizar las etiquetas y multiplicidades en el código PlantUML**
  - En `Workstation`: cambiar a `node "«device»\nEstación de Trabajo Clínica (PC / Laptop)\n[Multiplicidad: 1..*]" as Workstation`
  - En `Smartphone`: cambiar a `node "«device»\nSmartphone del Paciente (Android / iOS)\n[Multiplicidad: 1..*]" as Smartphone`
  - En `CloudServer`: especificar el proveedor cloud: `node "«cloud server»\nServidor Cloud VPS (DigitalOcean / AWS)\n[Ubuntu 22.04 LTS - 4 vCPU, 8GB RAM]" as CloudServer`
  - Dentro de `CloudServer`: incorporar el nodo `node "«executionEnvironment»\nDocker Engine 25.x (Contenedores)" as DockerHost` encapsulando los contenedores de Django REST, Celery y PostgreSQL.

- [x] **Step 3: Agregar Notas Explicativas UML con líneas de dependencia**
  Agregar notas en PlantUML:
  ```plantuml
  note "Aislamiento Multi-Tenant por Esquema PostgreSQL\nCertificados SSL Let's Encrypt Wildcard (*.sigepsi.online)\nDespliegue automatizado mediante Docker Compose" as N_Cloud
  N_Cloud .. CloudServer
  
  note "App compilada Flutter 3.x con SDK Jitsi nativo\nAlmacenamiento seguro en Keystore/Keychain\nNotificaciones push en background vía FCM v1" as N_Mobile
  N_Mobile .. Smartphone
  ```

- [x] **Step 4: Actualizar las descripciones textuales asociadas**
  Alinear los párrafos de la sección 7.2.1.1.3 para documentar la multiplicidad, contenedores y la política de red.

---

### Task 5: Incorporación de la Bitácora de Auditoría en Diagramas de Secuencia (Sección 7.2.1.3)

**Files:**
- Modify: `documentacion/sprint3.md:1625-2620`

**Interfaces:**
- Consumes: Directriz docente obligatoria (`CambiosProyecto2.md`, Línea 77: *"Esa bitácora en el diagrama de secuencia debe aparecer, por favor... por cada una de las acciones que van haciendo van registrándolo"*).
- Produces: Diagramas de secuencia y clases de análisis actualizados para CU11, CU12, CU13, CU17, CU21 y CU22, incorporando la línea de vida y mensajes hacia la entidad de Bitácora de auditoría.

- [x] **Step 1: Identificar los diagramas de secuencia del Sprint 3 en `documentacion/sprint3.md`**
  Ubicar las secuencias de:
  - CU11 (Gestión y Cancelación de Citas Móviles)
  - CU12 (Despacho de Notificaciones Push FCM)
  - CU13 (Teleconsulta WebRTC Nativa)
  - CU17 (Tareas Terapéuticas y Mood Tracker)
  - CU21 (Clasificación Asistiva de Motivos por IA)
  - CU22 (Matching Multivariable con Validación Humana)

- [x] **Step 2: Incorporar `CE_BitacoraAuditoria` en CU11 (Cancelación de Citas)**
  En el diagrama PlantUML de CU11 (líneas 1730-1780):
  - Añadir participante: `participant "CE_BitacoraAuditoria\n(PostgreSQL)" as ce_bitacora`
  - Añadir mensaje dentro del bloque de cancelación confirmada:
    `ctrl -> ce_bitacora : registrar_evento_auditoria(usuario_id, 'CANCELACION_CITA', cita_id, 'Cancelada por paciente >24h')`
    `ce_bitacora --> ctrl : evento_auditado(log_id)`

- [x] **Step 3: Incorporar `CE_BitacoraAuditoria` en CU12 (Notificaciones Push FCM)**
  Añadir participante `ce_bitacora` y mensaje:
  `ctrl -> ce_bitacora : registrar_despacho_push(cita_id, token_id, 'DESPACHADO_EXITOSO')`

- [x] **Step 4: Incorporar `CE_BitacoraAuditoria` en CU13, CU17, CU21 y CU22**
  Asegurar que cada flujo exitoso registre formalmente la tupla de auditoría inmutable antes del retorno hacia la interfaz de usuario.

- [x] **Step 5: Actualizar los diagramas de clases de análisis (BCE/VOPC) correspondientes**
  Verificar que `CE_BitacoraAuditoria` figure en los modelos estáticos VOPC de cada caso de uso.

---

### Task 6: Trazabilidad de Continuidad e Incrementos en Sprint Review (Sección 7.4)

**Files:**
- Modify: `documentacion/sprint3.md:4039-4080`

**Interfaces:**
- Consumes: Criterio docente (`CambiosProyecto1.md`, Líneas 35-39: justificación formal de tareas transferidas entre Sprints para evidenciar continuidad).
- Produces: Nueva sección `7.4.1 Trazabilidad de Tareas e Incremento Acumulado entre Sprints` en la Revisión del Sprint.

- [x] **Step 1: Leer la sección 7.4 actual**
  Verificar que actualmente solo contiene la tabla de presentación del incremento y la firma del PO.

- [x] **Step 2: Insertar la subsección de Continuidad y Traspaso de Tareas**
  Redactar e insertar una tabla formal con el historial de traspaso:
  - **Módulo Móvil de Pacientes:** Diseñado conceptualmente al cierre del Sprint 2; transferido formalmente al Sprint 3 para su implementación nativa completa en Flutter 3.x (`SP3-68` a `SP3-76`).
  - **Servicio Automatizado de Push (CU12):** Notificaciones por correo concluidas en Sprint 1; transferido al Sprint 3 para refinamiento y acoplamiento con la pasarela Firebase Cloud Messaging (FCM v1) en background.
  - **Módulos Cognitivos de IA (CU21 y CU22):** Chatbot básico concluido en Sprint 2; transferido al Sprint 3 para desarrollo del pipeline NLP de clasificación diagnóstica y algoritmo multivariable de matching con consola HITL.

- [x] **Step 3: Documentar la justificación formal del cumplimiento de continuidad**
  Añadir texto explícito indicando que ninguna tarea fue clonada sin justificación, garantizando la trazabilidad histórica exigida por la cátedra.

---

### Task 7: Rebalanceo Realista de Horas: Estimación vs. Realización y Gráficos (Secciones 7.6 y 7.7)

**Files:**
- Modify: `documentacion/sprint3.md:4118-4240`

**Interfaces:**
- Consumes: Crítica docente (`CambiosProyecto1.md`, Líneas 237-241: *"Esta hora no debe ser la misma de allá... Bueno, por lo menos no tenemos las horas igualitas"*).
- Produces: Tabla 7.7.1 recalibrada con variaciones reales ($\Delta h \neq 0$) alineadas a los incidentes documentados en el Daily Scrum, con actualización sincronizada del Burndown (7.6.1) y la comparativa por integrante (7.7.2).

- [x] **Step 1: Analizar los obstáculos reales del Daily Scrum (7.3)**
  Revisar los problemas reales experimentados:
  - Configuración de Gradle/Kotlin en emulador (`SP3-68`): tomó 4.5h en vez de 4.0h ($+0.5$h).
  - Renovación de token JWT en storage seguro (`SP3-69`): tomó 7.5h en vez de 7.0h ($+0.5$h).
  - Pruebas QA móvil con Keystore (`SP3-70`): tomó 3.5h en vez de 3.0h ($+0.5$h).
  - Prototipado Figma UI/UX (`SP3-71`): se resolvió rápido en 3.5h en vez de 4.0h ($-0.5$h).
  - Zonas horarias UTC y FCM (`SP3-72`): tomó 9.0h en vez de 8.0h ($+1.0$h).
  - Pruebas QA de notificaciones (`SP3-73`): tomó 3.0h (sin variación).
  - Wireframes de teleconsulta (`SP3-74`): tomó 3.5h en vez de 4.0h ($-0.5$h).
  - Integración SDK Jitsi Meet (`SP3-75`): tomó 9.0h en vez de 8.0h ($+1.0$h).
  - Testing WebRTC (`SP3-76`): tomó 3.5h en vez de 3.0h ($+0.5$h).
  - Calibración de pesos IA (`SP3-77`): tomó 9.0h en vez de 8.0h ($+1.0$h).
  - Pruebas BDD de IA (`SP3-78`): tomó 4.5h en vez de 4.0h ($+0.5$h).

- [x] **Step 2: Actualizar la Tabla 7.7.1 de Esfuerzo por Tarea**
  Reemplazar los valores artificiales de 0.0 hr por los valores reales, actualizando las justificaciones detalladas:
  - Total Estimado: 59.0 hr.
  - Total Real: 62.5 hr (Variación global: $+3.5$ hr, 105.9% de esfuerzo, perfectamente realista).

- [x] **Step 3: Ajustar la Tabla y Gráfica del Sprint Burndown (7.6.1)**
  Sincronizar las horas quemadas por día en la tabla 7.6.1 y la curva ASCII para reflejar con precisión el consumo acumulado de 62.5 horas.

- [x] **Step 4: Actualizar la Gráfica de Esfuerzo por Integrante (7.7.2)**
  Reflejar los nuevos totales reales por desarrollador en el gráfico ASCII y la tabla comparativa.

---

### Task 8: Enriquecimiento del Daily Scrum con Código de Tarea y % Avance (Sección 7.3)

**Files:**
- Modify: `documentacion/sprint3.md:3935-4035`

**Interfaces:**
- Consumes: Criterio docente (`CambiosProyecto1.md`, Línea 149: *"día tras día: «esta es mi tarea y este es mi avance»"*).
- Produces: Tablas individuales del Daily Scrum para los 6 integrantes con columnas explícitas `Tarea Asociada (ID)` y `% de Avance`.

- [x] **Step 1: Revisar la estructura actual de las 6 tablas del Daily Scrum**
  Verificar que actualmente las columnas son: `Fecha | ¿Qué hiciste ayer? | ¿Qué hiciste hoy? | Obstáculo`.

- [x] **Step 2: Reestructurar las cabeceras de tabla a 6 columnas**
  Modificar el formato a:
  `| Fecha | Tarea ID | ¿Qué hiciste ayer? | ¿Qué hiciste hoy? | % Avance | Obstáculo |`

- [x] **Step 3: Asignar a cada entrada la tarea del Backlog (`SP3-68` a `SP3-78`) y su progreso porcentual**
  Completar todas las filas de los 6 integrantes (Delgado, Mujica, Larrazabal, Condori, Romero, Velasco) vinculando las tareas técnicas y el porcentaje incremental de avance (ej. 25%, 50%, 75%, 100%).

---

### Task 9: Formalización de Reportes Operativos del Sprint 3 (Sección 7.2.2 y 7.8)

**Files:**
- Modify: `documentacion/sprint3.md:3320-3350` y `documentacion/sprint3.md:4285-4330`

**Interfaces:**
- Consumes: Exigencia docente (`CambiosProyecto1.md`, Línea 257: *"Deben trabajar en la parte ya de emitir reportes... quiero ver la asistencia... tienen que empezar a lanzar"*).
- Produces: Documentación técnica y especificación de los 3 reportes analíticos de salida del Sprint 3 en formatos PDF y HTML.

- [x] **Step 1: Identificar las necesidades de reportería de los nuevos módulos del Sprint 3**
  Definir los 3 reportes esenciales:
  1. **Reporte R-SP3-01:** Ficha de Triaje Clínico y Asignación Asistida por IA (PDF / HTML) con justificación de matching y firma del coordinador.
  2. **Reporte R-SP3-02:** Informe Longitudinal de Estado de Ánimo y Adherencia Terapéutica (*Mood Tracker*) del paciente (PDF).
  3. **Reporte R-SP3-03:** Registro Operativo de Despacho de Notificaciones Push FCM y Confirmación de Citas (HTML / CSV).

- [x] **Step 2: Redactar e insertar la especificación de Reportes en la sección de Implementación (7.2.2)**
  Detallar los endpoints del backend (`/api/v1/reportes/triaje-ia/{id}/pdf/`, `/api/v1/reportes/mood-tracker/{id}/pdf/`), librerías utilizadas (`ReportLab` / `WeasyPrint`), parámetros de filtro y estructura visual del PDF resultante.

- [x] **Step 3: Actualizar la matriz de los 8 Criterios Generales de la Cátedra**
  Consolidar el Criterio 5 (Reportes) evidenciando cómo el Sprint 3 aporta reportes especializados para la experiencia móvil y la IA.

---

### Task 10: Guía de Demostración Técnica y Verificación para la Defensa Docente

**Files:**
- Modify: `documentacion/sprint3.md:4440-4459`

**Interfaces:**
- Consumes: Criterio docente (`CambiosProyecto2.md`, Línea 121: *"debe mostrar su código, debe mostrar su funcionalidad... debe demostrar cómo está avanzando"*).
- Produces: Anexo final con la Guía Rápida de Comprobación y Demostración en Vivo para la defensa ante la docente.

- [x] **Step 1: Redactar los comandos paso a paso para la defensa**
  Documentar:
  - Inicialización del backend Django con esquemas activos: `python manage.py runserver 0.0.0.0:8000`.
  - Verificación del script de siembra con 12 tenants: `python manage.py seed_sprint3 --verify`.
  - Ejecución de la aplicación móvil en Flutter: `flutter run -d chrome` o `flutter run -d emulator-5554`.
  - Ejecución de pruebas BDD automatizadas: `behave features/sprint3/` o `pytest backend/clinica/tests/test_ia.py`.

- [x] **Step 2: Probar los comandos localmente en PowerShell**
  Comprobar que los scripts y comandos referenciados existan y funcionen correctamente en el repositorio.

- [x] **Step 3: Guardar y validar el documento final consolidado**
  Revisar que `documentacion/sprint3.md` compile sin errores de sintaxis Markdown y conserve todos los enlaces y diagramas intactos.

---

## Self-Review

- **Spec coverage:** El plan cubre el 100% de las 15 categorías de observaciones extraídas de las transcripciones docentes (`Cambios_Y_Observaciones_Docente_Sprint3.md`).
- **Step scan:** Cada tarea contiene pasos concretos, verificables e independientes con archivos específicos e interfaces definidas.
- **Consistency:** Todos los nombres de clases, entidades, esquemas y componentes coinciden con la nomenclatura oficial del proyecto SIGEPSI (`CU12`, `CU21`, `CU22`, `SP3-68` a `SP3-78`).
- **Review Focus:** Se atienden los cinco riesgos más críticos señalados por la docente (Multiplicidad en Despliegue, Capa 4 de Software de Sistema, Bitácora en Secuencias, Variación realista en Horas, URL/QR de acceso).
