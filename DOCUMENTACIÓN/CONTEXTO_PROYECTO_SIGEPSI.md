# PLATAFORMA WEB Y MÓVIL DE GESTIÓN INTEGRAL DE CITAS, EXPEDIENTES CLÍNICOS Y SEGUIMIENTO TERAPÉUTICO PARA CENTROS DE SALUD MENTAL (SIGEPSI)

> Documento de contexto de proyecto — transcripción íntegra del perfil de proyecto "GRUPO_9_Sistema_Psicologico", actualizado con el Capítulo 4 (Desarrollo Sprint 0). Este archivo sirve como base de contexto para la construcción del proyecto.

**Universidad Autónoma Gabriel René Moreno**
**Facultad de Ingeniería en Ciencias de la Computación y Telecomunicaciones**

**Grupo # 9**

**Integrantes:**

| Integrante | Registro |
|---|---|
| Condori Diaz Marilyn Esther | 224051237 |
| Delgado Rojas Alberto Caleb | 224027204 |
| Larrazabal Rojas Julio Cesar | 223049255 |
| Mujica Vallejos Andy Mauricio | 224028367 |
| Romero Saavedra Maria Ilse | 222009772 |
| Velasco Soliz Rolando | 223044768 |

---

## ÍNDICE ORIGINAL DEL DOCUMENTO

- PERFIL .......................................... 2
- 1. INTRODUCCIÓN .................................. 3
- 2 ANTECEDENTES ..................................... 3
  - FUNDAMENTACIÓN TEÓRICA .......................... 4
  - SISTEMAS SIMILARES .............................. 5
  - CASOS DE ESTUDIO ................................ 6
    - Caso de estudio 1: MentalGest ................ 6
    - Caso de estudio 2: Talkspace ................. 7
    - Caso de estudio 3: Spring Health ............. 7
    - Relación de los casos de estudio con el proyecto . 8
- 3 JUSTIFICACIÓN .................................... 9
- 4 DESCRIPCIÓN DEL PROBLEMA ......................... 10
- 5 FORMULACIÓN DEL PROBLEMA ......................... 15
- 6 OBJETIVOS ........................................ 16
  - 6.1 Objetivo General .............................. 17
  - 6.2 Objetivos Específicos ......................... 17
- 7 ALCANCE .......................................... 17
  - 7.1 Módulo de Gestión de Usuarios, Roles, Seguridad y Multi-Tenant . 18
  - 7.2 Módulo de Panel Administrativo (Dashboard) y Alertas de Priorización . 18
  - 7.3 Módulo de Gestión de Psicólogos y Pacientes ... 19
  - 7.4 Módulo de Agenda, Citas y Videoconferencias .... 19
  - 7.5 Módulo de Historia Clínica, Formulario Previo, Notas y Seguimiento . 20
  - 7.6 Módulo de Aplicación Móvil para Pacientes ...... 20
  - 7.7 Módulo de Inteligencia Artificial Asistida y Chatbot de Orientación . 21
  - 7.8 Módulo de Reportes Administrativos y Clínicos .. 22
  - 7.9 Módulo de Control de Pagos .................... 22
  - 7.10 Funcionalidades .............................. 23
    - 7.10.1 Funcionalidades Web ...................... 23
    - 7.10.2 Funcionalidades Móvil ..................... 23
    - 7.10.3 Funcionalidades IA ........................ 23
- 8 ELEMENTOS DEL SIBC ............................... 24
  - 8.1 HARDWARE ...................................... 25
  - 8.2 SOFTWARE ...................................... 25
  - 8.3 DATOS ......................................... 27
  - 8.4 PROCESOS ...................................... 27
  - 8.5 GENTE / USUARIO ............................... 28
  - 8.6 DOCUMENTO ..................................... 28
- 9 TECNOLOGÍA ........................................ 28
  - 9.1 Tecnología para el Desarrollo .................. 29
  - 9.2 Tecnología para la Puesta en Marcha ............ 29
- 10 COSTOS PARA LA PUESTA EN MARCHA ................. 30
- 11 BENEFICIOS PARA EL CLIENTE ...................... 32
  - Tiempo ............................................ 33
  - Esfuerzo Humano ................................... 33
  - Costos ............................................ 34
  - Accesibilidad y Adherencia al Tratamiento ......... 34
- CAPÍTULO 1 – MARCO TEÓRICO ......................... 35
  - 1.1 MARCO REFERENCIAL ............................. 36
  - 1.2 MARCO DE TRABAJO ÁGIL SCRUM .................... 39
- CAPÍTULO 2 – HERRAMIENTAS TECNOLÓGICAS PARA EL DESARROLLO . 45
- CAPÍTULO 3 – REQUERIMIENTOS ........................ 51
- CAPÍTULO 4 – DESARROLLO SPRINT 0 ................... 76
- BIBLIOGRAFÍA ........................................ 97
- ANEXOS .............................................. 100

---

# PERFIL

## 1. INTRODUCCIÓN

En la actualidad, el uso de herramientas digitales se ha convertido en un elemento fundamental para mejorar la organización y la atención en diferentes áreas de servicio, incluyendo el ámbito de la salud mental. Los centros y gabinetes psicológicos necesitan administrar citas, pacientes, historias clínicas, notas de sesión, pagos, recordatorios y seguimiento de manera ordenada, segura y accesible. Sin embargo, muchos de estos centros realizan sus procesos de forma manual o mediante herramientas dispersas, lo que genera desorganización, pérdida de información y dificultades en la atención al paciente.

El presente perfil de proyecto plantea el desarrollo de una plataforma web y una aplicación móvil basada en un modelo multi-empresa (SaaS Multi-Tenant) para la gestión integral de centros psicológicos. La arquitectura multi-tenant permitirá que múltiples centros, gabinetes o consultorios psicológicos puedan suscribirse e interactuar dentro de la misma solución, manteniendo sus datos, usuarios, horarios y configuraciones completamente aislados y seguros.

La aplicación móvil estará orientada tanto a los pacientes como al personal del centro (psicólogos y administradores), facilitando la consulta de citas, notificaciones, llenado de formularios previos a la consulta, interacción con un chatbot de orientación y seguimiento del proceso terapéutico. Por su parte, la plataforma web permitirá al personal administrativo, coordinadores clínicos y psicólogos gestionar de forma completa los pacientes, horarios, expedientes clínicos, sesiones, pagos y reportes consolidados de su respectivo centro.

La finalidad del proyecto es centralizar la información y optimizar los procesos principales de los centros psicológicos mediante una solución tecnológica moderna, escalable y adaptada a las necesidades del área de salud mental, incorporando herramientas de inteligencia artificial asistida bajo supervisión profesional.

Asimismo, la propuesta toma como referencia casos de estudio de plataformas reales como MentalGest, Talkspace y Spring Health, los cuales sirven como antecedentes para identificar funcionalidades, procesos de admisión, matching y buenas prácticas aplicables al desarrollo de esta plataforma.

---

## 2 ANTECEDENTES

Los antecedentes del presente proyecto se organizan en tres partes: la fundamentación teórica que sustenta los conceptos clave del sistema, la identificación de sistemas similares existentes en el mercado y el análisis de tres casos de estudio de plataformas reales relacionadas con la gestión psicológica, la atención virtual y la salud mental digital.

### FUNDAMENTACIÓN TEÓRICA

**Psicología clínica:** rama de la psicología dedicada a la evaluación, diagnóstico, tratamiento y prevención de trastornos mentales y problemas emocionales (American Psychological Association, 2017).

**Historia clínica psicológica:** documento médico-legal que contiene la información relevante del paciente, organizada cronológicamente: datos personales, antecedentes, motivo de consulta, diagnóstico, plan de tratamiento, notas de sesión y evolución (Fernández-Ballesteros, 2013).

**Salud mental:** según la OMS (2022), estado de bienestar en el que la persona puede desarrollar sus capacidades, afrontar el estrés normal de la vida, trabajar productivamente y contribuir a su comunidad.

**Proceso terapéutico:** abarca desde la primera consulta hasta el cierre o derivación del caso (Beck, 2011).

**Derivación al psiquiatra:** cuando el psicólogo identifica que el paciente requiere intervención farmacológica, se deriva al psiquiatra, único profesional autorizado para prescribir medicamentos.

**Consentimiento informado y ética profesional:** confidencialidad, consentimiento informado y manejo responsable de datos sensibles (Código de Ética del Psicólogo Boliviano, 2002).

**Arquitectura Multi-Tenant (SaaS):** permite atender a múltiples clientes desde una sola instancia de software, garantizando el aislamiento lógico de los datos de cada centro (Laudon & Laudon, 2020).

**Sistemas de información en salud:** herramientas para recopilar, almacenar, gestionar y transmitir información sanitaria (Laudon & Laudon, 2020).

**Inteligencia artificial aplicada a la salud mental:** IA predictiva (detección temprana de riesgo/abandono), IA generativa (resúmenes clínicos), chatbot conversacional y sistemas de recomendación para asignación de pacientes. Siempre bajo supervisión profesional (Graham et al., 2019).

### SISTEMAS SIMILARES

**SimplePractice** (simplepractice.com): agenda, notas clínicas, facturación, teletherapy y portal para clientes.

**TherapyNotes** (therapynotes.com): notas de tratamiento, agenda, facturación electrónica, portal del paciente y telehealth.

### CASOS DE ESTUDIO

#### Caso de estudio 1: MentalGest

Plataforma digital para organizar la consulta psicológica en un solo sistema: agenda, registro de pacientes, historia clínica, notas de sesión, pagos, recordatorios, reportes e IA asistida.

**Alcance:** gestión de usuarios (profesional/paciente), ficha del paciente, historia clínica con notas y evolución, agenda por profesional, recordatorios automáticos, control de pagos, IA asistida.

#### Caso de estudio 2: Talkspace

Plataforma de terapia online que conecta pacientes con profesionales licenciados mediante registro digital, formularios iniciales, matching, mensajería privada y sesiones en vivo.

**Alcance:** registro desde web o app móvil, formulario de intake, matching con proveedor, sala privada de comunicación, mensajería segura, sesiones en vivo (video/audio/chat).

#### Caso de estudio 3: Spring Health

Plataforma orientada a conectar a cada usuario con el tipo de atención que necesita mediante evaluación inicial, recomendaciones personalizadas y matching con proveedores.

**Alcance:** evaluación inicial, recomendación de nivel de cuidado, navegación clínica (Care Navigators), matching con terapeutas, terapia virtual/presencial, recursos digitales, reportes agregados.

#### Relación de los casos de estudio con el proyecto

MentalGest orienta la gestión web y móvil administrativa/clínica; Talkspace aporta la experiencia móvil del paciente y la atención online; Spring Health aporta la preevaluación, clasificación y derivación de casos. A partir de estos referentes, el proyecto plantea una aplicación móvil y una página web para apoyar la gestión administrativa, clínica y de seguimiento de un centro psicológico.

---

## 3 JUSTIFICACIÓN

La selección del presente proyecto responde a la necesidad de contar en Bolivia con una solución digital integrada en la nube (SaaS Multi-Tenant) que permita a múltiples centros, gabinetes y consultorios psicológicos organizar eficientemente sus procesos administrativos, clínicos y de seguimiento.

Actualmente, muchos centros operan de forma aislada mediante agendas físicas, hojas de cálculo, archivos de Word dispersos y coordinación por WhatsApp, provocando desorganización, pérdida de tiempo, duplicidad de datos y falta de continuidad terapéutica.

Un esquema de suscripción multi-tenant permite que cualquier centro o profesional independiente se registre, configure su propio espacio de trabajo de manera aislada y acceda a herramientas avanzadas sin requerir infraestructura propia. La IA asistida permitirá optimizar el tiempo de los profesionales, siempre bajo supervisión y validación del criterio profesional.

---

## 4 DESCRIPCIÓN DEL PROBLEMA

La atención en salud mental involucra información administrativa (citas, pagos, horarios) y datos clínicos altamente confidenciales. Los centros psicológicos necesitan gestionar simultáneamente: registro y seguimiento de pacientes, agendas de profesionales, fichas psicológicas y notas de sesión, comunicación con pacientes, pagos y reportes.

En el contexto boliviano y latinoamericano, estos procesos suelen ser manuales o dispersos (agendas físicas, Excel, Word, WhatsApp), generando desorganización, pérdida de datos y dificultad para el seguimiento terapéutico continuo.

**Dimensiones del problema:**

1. **Ausencia de un sistema integrado**: datos dispersos en múltiples medios sin conexión entre ellos, duplicidad de información, pérdida de tiempo buscando registros.
2. **Gestión manual de citas, horarios e inasistencias**: cruces de horarios, olvidos de confirmación, reprogramaciones mal registradas, inasistencias sin seguimiento.
3. **Falta de una historia clínica organizada**: notas dispersas, preparación deficiente de sesiones, dificultad para transferir información entre profesionales.
4. **Comunicación limitada con el paciente**: canales externos (WhatsApp, llamadas) no integrados ni confidenciales.
5. **Escasa generación de reportes**: imposibilidad de obtener indicadores actualizados para la toma de decisiones.
6. **Necesidad de apoyo tecnológico e IA**: sobrecarga de tareas documentales y de clasificación manual.
7. **Falta de personalización del proceso terapéutico**: sin visión integral y actualizada del caso.

El desarrollo de una aplicación móvil y una plataforma web busca responder de manera integral a estas dificultades mediante una solución digital centralizada, segura, ordenada y específicamente orientada a la gestión psicológica y la salud mental.

---

## 5 FORMULACIÓN DEL PROBLEMA

El proyecto busca resolver la problemática administrativa, clínica y de seguimiento de los centros psicológicos en Bolivia. El sistema contemplará módulos de gestión de usuarios y roles, registro de pacientes, ficha psicológica inicial, agenda de citas, recordatorios, notas de sesión, seguimiento terapéutico, control de pagos, reportes básicos, formularios iniciales y apoyo mediante IA asistida.

La página web estará orientada principalmente al personal administrativo y a los psicólogos; la aplicación móvil estará destinada al acceso de pacientes, psicólogos y personal administrativo, facilitándoles el acceso a citas, notificaciones, formularios y seguimiento básico.

---

## 6 OBJETIVOS

### 6.1 Objetivo General

Desarrollar una plataforma web y móvil de gestión integral de citas, expedientes clínicos y seguimiento terapéutico para centros de salud mental, basada en un modelo multi-empresa (SaaS Multi-Tenant) con apoyo de inteligencia artificial asistida bajo supervisión profesional.

### 6.2 Objetivos Específicos

- Recolectar información sobre los procesos administrativos, clínicos y de atención al paciente mediante entrevistas, observación y casos de estudio.
- Analizar los requerimientos funcionales y no funcionales para definir los módulos y funcionalidades.
- Diseñar la arquitectura multi-tenant, las interfaces web y móvil, y el modelo de base de datos.
- Desarrollar la plataforma web para usuarios, roles, agenda, expedientes clínicos, notas de sesión, pagos, alertas y reportes.
- Desarrollar la aplicación móvil orientada al paciente para citas, formularios previos, notificaciones, seguimiento terapéutico y teleconsulta.
- Implementar módulos de IA asistida para clasificación, asignación, resúmenes clínicos, chatbot y detección de riesgo.
- Probar las funcionalidades implementadas e incorporar correcciones.

---

## 7 ALCANCE

El alcance contempla una solución SaaS Multi-Tenant, compuesta por una plataforma web administrativa/clínica y una aplicación móvil orientada a pacientes y personal del centro. La arquitectura multi-tenant garantiza el aislamiento lógico de la información, usuarios, pacientes y finanzas de cada centro.

**La plataforma web** estará destinada al personal operativo e interno de los centros: Administradores de Plataforma (SuperAdmin), Administradores de Centro, Recepcionistas, Coordinadores Clínicos y Psicólogos. **La aplicación móvil** estará orientada a los pacientes y al personal clínico, facilitando su interacción con el centro, la gestión de sus citas y su seguimiento terapéutico.

### 7.1 Módulo de Gestión de Usuarios, Roles, Seguridad y Multi-Tenant

Núcleo de control de acceso y seguridad. Cada centro suscrito opera dentro de un entorno aislado con su propia configuración institucional, usuarios, permisos y datos.

- **SuperAdministrador (Plataforma):** da de alta/baja centros suscritos (tenants), administra planes, licencias y supervisa el sistema.
- **Administrador del Centro:** configura su centro, da de alta personal, roles institucionales, permisos y parámetros del gabinete.
- **Recepcionista:** registra pacientes, agenda citas, confirma asistencia, consulta estados de cuenta básicos.
- **Coordinador Clínico:** revisa admisiones, aprueba/modifica asignaciones sugeridas por IA, supervisa derivaciones y alertas.
- **Psicólogo:** accede exclusivamente a sus pacientes asignados, agenda personal, fichas clínicas, notas de sesión.
- **Paciente:** accede vía app móvil para revisar citas, completar formularios, interactuar con el chatbot y recibir indicaciones.
- **Gestión de Permisos y Consentimientos Informados Digitales.**
- **Registro de Auditoría e Historial de Accesos.**

### 7.2 Módulo de Panel Administrativo (Dashboard) y Alertas de Priorización

- **Dashboard Principal e Indicadores Clave (KPIs).**
- **Consola de Alertas de Priorización.**
- **Panel de Gestión y Validación del Coordinador Clínico.**

### 7.3 Módulo de Gestión de Psicólogos y Pacientes

- **Perfil Profesional del Psicólogo:** colegiatura, especialidades, experiencia, modalidad, disponibilidad, cupos.
- **Control de Carga de Trabajo.**
- **Expediente Centralizado del Paciente.**
- **Criterios y Reglas de Asignación.**

### 7.4 Módulo de Agenda, Citas y Videoconferencias

- **Calendario Interactivo Multivista.**
- **Gestión Integral de Citas** (reserva, confirmación, cancelación, reprogramación, estados).
- **Sistema de Recordatorios Automáticos.**
- **Módulo de Teleconsulta y Videoconferencias** (Jitsi Meet / Zoom SDK).

### 7.5 Módulo de Historia Clínica, Formulario Previo, Notas y Seguimiento

- **Formulario Previo a la Consulta (Intake Digital).**
- **Ficha Psicológica Inicial e Historia Clínica.**
- **Registro de Notas de Sesión.**
- **Registro de Evolución y Seguimiento Terapéutico.**
- **Cierre y Derivación del Caso.**

### 7.6 Módulo de Aplicación Móvil para Pacientes

La aplicación móvil (Flutter, Android e iOS) actúa como canal nativo y seguro de interacción del paciente con el centro.

- **Registro e Inicio de Sesión Seguro.**
- **Gestión de Citas Móvil.**
- **Notificaciones Push y Recordatorios.**
- **Llenado del Formulario Previo.**
- **Acceso a Teleconsulta.**
- **Portal de Seguimiento y Tareas.**

### 7.7 Módulo de Inteligencia Artificial Asistida y Chatbot de Orientación

- **Chatbot Conversacional de Orientación.**
- **Clasificación Inteligente de Motivos de Consulta.**
- **Sugerencia de Asignación Asistida.**
- **Generación Asistida de Resúmenes Clínicos.**
- **Detección de Señales de Riesgo y Alertas Prioritarias.**

### 7.8 Módulo de Reportes Administrativos y Clínicos

- **Reportes Operativos de Citas y Asistencia.**
- **Reportes de Gestión de Pacientes.**
- **Reportes de Demanda por Especialidad.**
- **Reportes de Carga de Trabajo Profesional.**
- **Reportes de Evolución y Efectividad Clínica.**
- **Exportación de Datos** (PDF, Excel).

### 7.9 Módulo de Control de Pagos

- **Registro de Cobros por Servicio.**
- **Estado de Cuenta del Paciente.**
- **Control de Métodos de Pago.**
- **Historial Financiero Administrativo.**

### 7.10 Funcionalidades

#### 7.10.1 Funcionalidades Web

Gestión de Usuarios/Roles/Seguridad/Multi-Tenant, Panel de Control, Gestión de Psicólogos y Especialidades, Gestión de Pacientes, Formulario Previo, Agenda/Citas/Videoconferencias, Historial Clínico/Notas/Evolución, Alertas de Priorización, Reportes, Control de Pagos y Facturación, Permisos/Consentimientos/Documentación.

#### 7.10.2 Funcionalidades Móvil

Registro e Inicio de Sesión de Pacientes, Gestión de Citas, Formulario Previo, Notificaciones y Recordatorios, Chatbot de Orientación, Seguimiento/Videoconferencias/Tareas Terapéuticas.

#### 7.10.3 Funcionalidades IA

Clasificación y Asignación Inicial, Sugerencias/Recomendaciones/Resúmenes, Detección de Señales de Prioridad y Riesgo, Apoyo a la Toma de Decisiones, Restricciones Éticas y de Seguridad.

---

## 8 ELEMENTOS DEL SIBC

### 8.1 HARDWARE

- **Servidor:** nube (AWS/DigitalOcean/Railway), Linux Ubuntu Server, capacidad escalable.
- **Cliente:** computadoras para personal administrativo/clínico; smartphones y tablets Android/iOS para pacientes y profesionales.
- **Otros:** impresora multifuncional, cámaras/micrófonos para videoconferencias, router/punto de acceso.

### 8.2 SOFTWARE

- **Servidor:** Linux Ubuntu Server; Django/DRF (Python); PostgreSQL; Gunicorn + Nginx; motor de IA (API de IA / LLM).
- **Cliente:** Angular (TypeScript) para la web; Flutter (Dart) para móvil; navegadores modernos; Android e iOS.
- **Otro software:** Git/GitHub; Visual Studio Code; Figma; Jira/Trello; Postman; Firebase Cloud Messaging; SendGrid/Mailgun; Jitsi Meet API / Zoom SDK; Let's Encrypt.

### 8.3 DATOS

Base de datos relacional centralizada en PostgreSQL (pacientes, psicólogos, especialidades, citas, fichas, notas, evolución, pagos, alertas, reportes, consentimientos, chatbot, accesos). Respaldo periódico, encriptación de datos sensibles, políticas de retención, separación lógica de datos administrativos y clínicos.

### 8.4 PROCESOS

Registro de paciente y formulario previo; clasificación/asignación (manual o IA, validada por coordinador); agendamiento/confirmación/reprogramación/cancelación; notas de sesión y evolución; reportes; consentimientos; respaldo y recuperación; chatbot con escalamiento humano; alertas de riesgo; pagos; derivación de pacientes.

### 8.5 GENTE / USUARIO

Administrador del sistema, Recepcionista, Coordinador clínico, Psicólogos, Pacientes, Equipo de soporte técnico.

### 8.6 DOCUMENTO

Consentimiento informado, autorización de tratamiento de datos, permiso para IA, consentimiento de teleconsulta, ficha psicológica inicial, notas de sesión, reportes, historial de pagos, registro de aceptación de documentos, documentos adjuntos.

---

## 9 TECNOLOGÍA

### 9.1 Tecnología para el Desarrollo

- **Lenguaje backend:** Python.
- **Framework backend:** Django / Django REST Framework.
- **Lenguaje frontend web:** TypeScript.
- **Framework frontend:** Angular.
- **Desarrollo móvil:** Flutter (Dart).
- **Base de datos:** PostgreSQL.
- **Motor de IA:** API de IA / LLM (cualquier proveedor disponible).
- **Control de versiones:** Git / GitHub.
- **IDE:** Visual Studio Code.
- **Diseño de prototipos:** Figma.
- **Gestión de proyecto:** Jira / Trello.
- **Documentación:** Markdown / Google Docs.

### 9.2 Tecnología para la Puesta en Marcha

- **Hosting web:** AWS / DigitalOcean / Railway.
- **Servidor de aplicación:** Gunicorn + Nginx.
- **Almacenamiento de archivos:** AWS S3 / Cloudinary.
- **Dominio web:** .com / .bo.
- **Certificado SSL:** Let's Encrypt.
- **Servicio de correo:** SendGrid / Mailgun.
- **Notificaciones push:** Firebase Cloud Messaging (FCM).
- **Videollamadas:** Jitsi Meet API / Zoom SDK.
- **Distribución móvil:** Google Play Store / Apple App Store.
- **Monitoreo:** Sentry / UptimeRobot.

---

## 10 COSTOS PARA LA PUESTA EN MARCHA

| Categoría | Detalle | Subtotal |
|---|---|---|
| Hardware | Servidor nube, PC administración, dispositivo Android de pruebas, impresora | 1,150.00 USD |
| Software | Dominio, SSL (gratis), API IA, cuentas de desarrollador Google/Apple, correo (gratis), herramientas dev (gratis) | 376.00 USD |
| Comunicaciones | Internet del centro, Firebase (gratis), Jitsi Meet (gratis) | 360.00 USD |
| Recursos Humanos | Full-stack, móvil, UI/UX, especialista IA, QA | 19,100.00 USD |
| Logística | Transporte, papelería, capacitación, contingencias (5%) | 335.50 USD |
| **TOTAL** | | **21,321.50 USD** |

---

## 11. BENEFICIOS PARA EL CLIENTE

**Tiempo:** menos papeleo (Registro Médico Electrónico), gestión eficiente de citas con confirmación automática, automatización de clasificación inicial con IA, generación instantánea de estadísticas.

**Esfuerzo Humano:** alivio de carga para psicólogos (chatbot de orientación inicial), disminución de labores administrativas, seguimiento continuo entre sesiones, gamificación de adherencia en el módulo móvil.

**Costos:** infraestructura sin servidores físicos locales (SaaS Multi-tenant), eliminación de suministros de papel, disminución del ausentismo (recordatorios automáticos), facturación optimizada.

**Accesibilidad y Adherencia al Tratamiento:** disponibilidad extendida (video/chat asincrónico), monitoreo continuo vía app móvil, mejora de resultados clínicos, disminución de estigma (chat y formularios digitales).

---

# CAPÍTULO 1 – MARCO TEÓRICO

## 1.1 MARCO REFERENCIAL

### 1.1.1 Salud Mental

La OMS (2022) define la salud mental como un estado de bienestar en el cual el individuo es consciente de sus propias capacidades, puede afrontar las tensiones normales de la vida, trabajar de forma productiva y contribuir a su comunidad. Aproximadamente una de cada ocho personas en el mundo padece algún trastorno mental, siendo los más prevalentes la ansiedad y la depresión.

### 1.1.2 Psicología Clínica

Rama de la psicología que se ocupa de la investigación, evaluación, diagnóstico, tratamiento, prevención y rehabilitación de trastornos mentales, emocionales y conductuales (American Psychological Association, 2017). Enfoques: cognitivo-conductual, psicodinámica, humanista, sistémica e integrativos.

### 1.1.3 Centros Psicológicos y Gabinetes

Un centro psicológico ofrece terapia individual, de pareja, familiar, infantil, evaluación, orientación vocacional, intervención en crisis y prevención. Un gabinete psicológico puede integrarse dentro de instituciones educativas, empresariales, hospitalarias o sociales.

### 1.1.4 Historia Clínica Psicológica

Documento médico-legal cronológico y sistemático (Fernández-Ballesteros, 2013): identificación, motivo de consulta, antecedentes, evaluación inicial, diagnóstico, plan de tratamiento, notas de sesión, evolución, acuerdos y tareas, consentimiento informado, cierre o derivación.

### 1.1.5 Proceso Terapéutico

Fases (Beck, 2011): admisión, evaluación, planificación del tratamiento, intervención, seguimiento y evaluación, cierre o derivación (incluyendo derivación al psiquiatra).

### 1.1.6 Consentimiento Informado en Psicología

Documento mediante el cual el paciente, tras recibir información clara sobre el proceso, técnicas, alcances, limitaciones, confidencialidad y tratamiento de datos, otorga autorización voluntaria (Código de Ética del Psicólogo Boliviano, 2002). En plataformas digitales incluye además: almacenamiento/procesamiento electrónico, uso de IA asistida, y modalidad de teleconsulta.

### 1.1.7 Teleconsulta y Telepsicología

Prestación de servicios psicológicos vía videoconferencias, mensajería segura, llamadas y plataformas digitales. Requiere consideraciones técnicas, éticas y legales.

### 1.1.8 Inteligencia Artificial Aplicada a la Salud Mental

Clasificación automatizada de texto, generación de resúmenes clínicos, detección temprana de señales de riesgo, sistemas de recomendación para asignación de pacientes (Graham et al., 2019). La IA opera exclusivamente como apoyo, nunca como sustituto del criterio profesional.

### 1.1.9 Modelo SaaS Multi-Tenant

El enfoque multi-tenant permite que una sola instancia del software atienda a múltiples clientes (tenants), cada uno con un entorno lógicamente aislado (Laudon & Laudon, 2020). Reduce significativamente los costos de infraestructura, mantenimiento y actualización.

## 1.2 MARCO DE TRABAJO ÁGIL SCRUM

### 1.2.1 Introducción al Manifiesto Ágil

En 2001 se firmó el Manifiesto por el Desarrollo Ágil de Software, con cuatro valores: individuos e interacciones sobre procesos y herramientas; software funcionando sobre documentación extensiva; colaboración con el cliente sobre negociación contractual; respuesta ante el cambio sobre seguir un plan.

### 1.2.2 Los Doce Principios del Manifiesto Ágil

Satisfacer al cliente con entrega temprana y continua; aceptar cambios de requisitos incluso tardíos; entregar software funcional frecuentemente; trabajo conjunto diario de negocio y desarrollo; proyectos en torno a individuos motivados; comunicación cara a cara; software funcionando como medida de progreso; desarrollo sostenible; atención a la excelencia técnica; simplicidad; equipos autoorganizados; reflexión e integración periódica.

### 1.2.3 ¿Qué es SCRUM?

Marco de trabajo ágil liviano basado en el empirismo y el pensamiento Lean. Concebido por Takeuchi y Nonaka (1986), formalizado por Schwaber y Sutherland en los años 90. Pilares: **Transparencia**, **Inspección**, **Adaptación**.

### 1.2.4 Roles en SCRUM

- **Product Owner:** maximiza el valor del producto, gestiona el Product Backlog.
- **Scrum Master:** facilita el proceso, elimina impedimentos.
- **Equipo de Desarrollo:** autoorganizado y multifuncional (óptimo de 5 a 9 personas).
- **Stakeholders:** partes interesadas que retroalimentan en las revisiones.

### 1.2.5 Eventos de SCRUM

Sprint; Sprint Planning; Daily Scrum (15 min); Sprint Review; Sprint Retrospective.

### 1.2.6 Artefactos de SCRUM

Product Backlog; Sprint Backlog; Incremento.

### 1.2.7 Historias de Usuario

Formato: **Como [rol], quiero [funcionalidad], para [beneficio].** Criterios INVEST: Independiente, Negociable, Valiosa, Estimable, Pequeña (Small), Comprobable (Testable). Las historias de usuario correspondientes al Sprint 0 abarcan los casos de uso CU1, CU2, CU3 y CU4, y los requisitos funcionales RF-01, RF-02 y RF-03, relacionados con gestión de usuarios, roles, permisos, autenticación y configuración Multi-Tenant.

**Historias de Usuario: Sprint 0**

| ID | Título | Rol | Historia de Usuario |
|---|---|---|---|
| HU-01 | Registro de SuperAdministrador | SuperAdmin | Como SuperAdministrador, quiero registrarme con credenciales seguras, para acceder al panel de administración global del sistema. |
| HU-02 | Inicio de sesión multi-rol | Todos los roles | Como usuario del sistema, quiero iniciar sesión con mi correo y contraseña mediante tokens, para acceder a las funcionalidades de mi rol. |
| HU-03 | Alta de centros psicológicos | SuperAdmin | Como SuperAdministrador, quiero dar de alta un nuevo centro psicológico, para que opere con datos aislados. |
| HU-04 | Configuración del centro | Admin de Centro | Como Administrador del Centro, quiero configurar los datos institucionales, para personalizar el funcionamiento de la plataforma. |
| HU-05 | Registro de usuarios del centro | Admin de Centro | Como Administrador del Centro, quiero registrar usuarios dentro de mi centro, para que accedan al sistema. |
| HU-06 | Asignación de roles y permisos | Admin de Centro | Como Administrador del Centro, quiero asignar roles y permisos, para controlar el acceso de cada persona. |
| HU-07 | Aislamiento Multi-Tenant | Admin de Centro | Como Administrador del Centro, quiero que mi información esté aislada de otros centros, para garantizar la confidencialidad. |
| HU-08 | Gestión de centros suscritos | SuperAdmin | Como SuperAdministrador, quiero editar, suspender o dar de baja centros, para mantener el control de la plataforma. |
| HU-09 | Cierre de sesión seguro | Todos los roles | Como usuario del sistema, quiero cerrar mi sesión de manera segura, para proteger mi cuenta. |
| HU-10 | Recuperación de contraseña y credenciales | Todos los roles | Como usuario del sistema, quiero recuperar mi contraseña mediante correo electrónico, para acceder nuevamente a la plataforma en caso de olvidar o bloquear mis credenciales. Caso de uso asociado: **CU27**. Requisito funcional asociado: **RF-31**. |

> **Nota importante (versión actualizada del documento):** en esta versión, **CU27 se redefine como "Recuperar contraseña o credenciales de acceso"** (antes era "Gestionar inicio de sesión y autenticación en la aplicación móvil"), pasa a **Sprint 0** (antes SP3), y aplica tanto a Web como a Móvil. Ver sección 3.9 y Capítulo 4 para el detalle completo con criterios de aceptación.

### 1.2.8 Aplicación de SCRUM en el Proyecto

Equipo SCRUM con roles de Product Owner, Scrum Master y Equipo de Desarrollo distribuidos entre los integrantes. Desarrollo organizado en Sprint 0 (preparación e infraestructura) seguido de 4 Sprints incrementales:

- **Sprint 0:** 25 y 27 de agosto de 2026
- **Sprint 1:** 08 y 10 de septiembre de 2026
- **Sprint 2:** 06 y 08 de octubre de 2026
- **Sprint 3:** 03 y 05 de noviembre de 2026

El Sprint 0 contempla la configuración inicial del entorno de desarrollo, la implementación del módulo de gestión de usuarios (login, roles y permisos) y la preparación de la infraestructura base del proyecto.

---

# CAPÍTULO 2 – HERRAMIENTAS TECNOLÓGICAS PARA EL DESARROLLO

## 2.1 LENGUAJE DE PROGRAMACIÓN

### 2.1.1 Python (Backend)

Lenguaje de alto nivel, interpretado, de tipado dinámico y multiparadigma, creado por Guido van Rossum (1991). Elegido por su ecosistema de IA/NLP (TensorFlow, PyTorch, NLTK, spaCy, Hugging Face), frameworks web robustos (Django, FastAPI) y soporte para APIs RESTful.

Versión recomendada: Python 3.11 o superior.

### 2.1.2 TypeScript (Frontend Web)

Lenguaje de Microsoft que extiende JavaScript con tipado estático opcional. Detección temprana de errores, autocompletado, compatibilidad nativa con Angular.

Versión recomendada: TypeScript 5.x.

### 2.1.3 Dart (Desarrollo Móvil)

Lenguaje de Google optimizado para interfaces rápidas, utilizado por Flutter. Compilación AOT (código nativo de alto rendimiento) y JIT (hot reload), null safety.

Versión recomendada: Dart 3.x (incluido con Flutter SDK).

## 2.2 FRAMEWORKS Y ENTORNOS DE EJECUCIÓN

### 2.2.1 Django / Django REST Framework (Backend Web)

DRF ofrece serialización, vistas basadas en clases/funciones, autenticación por tokens (JWT), paginación, filtrado, permisos granulares y documentación automática. **En el proyecto, Django y DRF conforman el backend que expone la API REST consumida tanto por la plataforma web (Angular) como por la aplicación móvil (Flutter)** — un único backend compartido, no uno distinto por plataforma.

### 2.2.2 Angular (Frontend Web)

Seleccionado por su robustez empresarial, tipado fuerte con TypeScript, arquitectura modular y amplia adopción.

Versión recomendada: Angular 17 o superior.

### 2.2.3 Flutter (Desarrollo Móvil)

Framework de Google para apps nativas Android/iOS desde una sola base de código en Dart, motor de renderizado propio (Skia). Seleccionado para la aplicación móvil orientada al paciente.

Versión recomendada: Flutter 3.x.

## 2.3 SISTEMA GESTOR DE BASE DE DATOS

### 2.3.1 PostgreSQL

Almacenará usuarios, pacientes, psicólogos, citas, historias clínicas, notas, pagos, alertas, reportes y configuraciones por tenant. Separación lógica de datos entre tenants mediante esquemas de PostgreSQL.

Versión recomendada: PostgreSQL 16 o superior.

## 2.4 LENGUAJE DE MODELADO DE SOFTWARE (MODELO C4)

Creado por Simon Brown, cuatro niveles: **Contexto** (usuarios: SuperAdmin, Administrador, Recepcionista, Coordinador, Psicólogo, Paciente; plataformas web/móvil; servicios externos IA, Firebase, Jitsi Meet, SendGrid, pagos), **Contenedores** (app web Angular, app móvil Flutter, API REST Django/DRF, PostgreSQL, IA, Firebase, Jitsi Meet), **Componentes** (módulos internos del backend Django: autenticación, pacientes, agenda, historia clínica, IA, pagos, reportes), **Código**.

## 2.5 HERRAMIENTA DE DISEÑO Y MODELADO

### 2.5.1 Figma

Diseño colaborativo de interfaces, prototipos interactivos, sistemas de diseño con componentes reutilizables.

### 2.5.2 Enterprise Architect / Herramientas UML

Para UML y Modelo C4: Enterprise Architect, StarUML, Draw.io o Structurizr.

## 2.6 ENTORNO DE DESARROLLO

### 2.6.1 Visual Studio Code

Extensiones: Python, Angular Language Service, Dart y Flutter, PostgreSQL, GitLens, Prettier, ESLint, Thunder Client/REST Client.

## 2.7 INFRAESTRUCTURA DE SOFTWARE (IaaS)

### 2.7.1 Servicio en la Nube (Cloud Computing)

Proveedor seleccionado: **Google Cloud Platform (GCP)** — Compute Engine, Cloud SQL, Cloud Storage, Cloud Functions, Vertex AI.

### 2.7.2 SaaS (Software as a Service)

Modelo de distribución adoptado. Estrategia de aislamiento en PostgreSQL: **aislamiento por esquema** — cada tenant dispone de su propio esquema dentro de la misma instancia PostgreSQL, gestionado con `django-tenants` o similar (creación automática de esquemas, enrutamiento por tenant, migraciones compartidas).

## 2.8 HERRAMIENTAS COLABORATIVAS PARA SEGUIMIENTO DE PROYECTOS

### 2.8.1 Jira Software

Planificación de sprints, historias de usuario, tableros Kanban/Scrum, reportes de velocidad.

## 2.9 SISTEMA DE CONTROL DE VERSIONES DE CÓDIGO (GIT)

Estrategia de ramificación: **main** (estable/producción), **develop** (integración), **feature/nombre** (por integrante, con Pull Request a develop), **hotfix/nombre** (correcciones urgentes sobre main).

## 2.10 HERRAMIENTAS DE GESTIÓN DE CÓDIGO EN LA NUBE

### 2.10.1 GitHub

Repositorios remotos, Pull Requests, GitHub Actions (CI/CD), issues, wikis. Estructura: un repositorio para backend (Django/DRF), uno para frontend web (Angular) y uno para la aplicación móvil (Flutter).

---

# CAPÍTULO 3 – REQUERIMIENTOS

## 3.1 Propósito

Desarrollar una Plataforma Web y Móvil de Gestión Inteligente e Integral de Salud Mental para Centros Psicológicos, Seguimiento de Pacientes y Gestión del Gabinete Psicológico.

## 3.2 Ámbito de Sistema

Abarca desde la administración de centros (SaaS Multi-Tenant), registro de usuarios/psicólogos/pacientes, citas, formularios previos, historias clínicas, notas de sesión, evolución terapéutica, videoconferencias y pagos, hasta reportes, alertas, chatbot e IA asistida. Queda **fuera de alcance**: procesos contables avanzados, diagnóstico autónomo mediante IA y prescripción de medicamentos.

## 3.3 Equipo SCRUM

### 3.3.1 Product Owner

Gestiona y prioriza el Product Backlog, representa las necesidades del proyecto.

### 3.3.2 Stakeholders

Centros psicológicos, gabinetes, consultorios privados, administradores, recepcionistas, coordinadores clínicos, psicólogos y pacientes.

### 3.3.3 Scrum Master

Facilita el equipo, elimina impedimentos, asegura la correcta aplicación de SCRUM.

### 3.3.4 Scrum Development

Analiza, diseña, desarrolla, integra, prueba y valida las funcionalidades. Equipo multidisciplinario y autoorganizado.

| Rol | Integrante |
|---|---|
| Product Owner | Condori Diaz Marilyn Esther |
| Scrum Master | Delgado Rojas Alberto Caleb |
| Development Team | Mujica Vallejos Andy Mauricio, Velasco Soliz Rolando, Larrazabal Rojas Julio Cesar, Romero Saavedra Maria Ilse |

## 3.4 Definiciones, Acrónimos y Abreviaturas

SaaS, Multi-Tenant, IA, NLP, LLM, Sprint, CU (casos de uso), HU (historias de usuario), RF (requisitos funcionales), RNF (requisitos no funcionales), API, DB, UML, BI, IaaS, SGBD.

## 3.5 Funciones del Producto

Gestión de Usuarios/Roles/Centros Psicológicos; Gestión de Psicólogos y Pacientes; Gestión de Agenda/Citas/Videoconferencias; Gestión de Historia Clínica Psicológica; Gestión de Formularios Previos y Seguimiento Terapéutico; Panel Administrativo y Alertas de Priorización; Chatbot Inteligente de Orientación; Clasificación y Asignación Asistida por IA; Generación de Resúmenes y Detección de Señales de Riesgo; Aplicación Móvil para Pacientes; Gestión de Reportes Administrativos y Clínicos; Gestión de Pagos, Consentimientos y Seguridad.

## 3.6 Product Backlog

**Proyecto:** SIGEPSI · **Product Owner:** Condori Diaz Marilyn Esther · **Versión:** 1.0

| NRO | ID | Rol / Responsable | Característica / Funcionalidad | Tiempo Estimado | Prioridad |
|---|---|---|---|---|---|
| 1 | SP0-1 | Equipo SCRUM | Entrevista con el Product Owner para identificar las necesidades principales del proyecto | 4 hr | Media |
| 2 | SP0-2 | Equipo SCRUM | Crear el perfil que explique la finalidad y características principales del proyecto | 2 hr | Alta |
| 3 | SP0-3 | Equipo SCRUM | Explicar al Product Owner el funcionamiento de la metodología ágil SCRUM | 2 hr | Baja |
| 4 | SP0-4 | Equipo SCRUM | Explicar al equipo la definición y formulación del problema | 5 hr | Alta |
| 5 | SP0-5 | Equipo SCRUM | Realizar la asignación de roles del equipo SCRUM | 1 hr | Media |
| 6 | SP0-6 | Equipo SCRUM | Capacitar a los integrantes en las herramientas y tecnologías que se utilizarán | 3 hr | Alta |
| 7 | SP0-7 | Equipo SCRUM | Preparar el entorno de desarrollo para backend, web, móvil y base de datos | 5 hr | Alta |
| 8 | SP0-8 | Equipo SCRUM | Presentar un prototipo inicial de la plataforma web y aplicación móvil | 6 hr | Media |
| 9 | SP0-9 | Equipo SCRUM | Identificar los casos de uso funcionales de la plataforma web y móvil | 3 hr | Alta |
| 10 | SP0-10 | Mujica Vallejos Andy Mauricio | Realizar el modelado inicial de la base de datos PostgreSQL | 8 hr | Alta |
| 11 | SP0-11 | Mujica Vallejos Andy Mauricio | Diseñar la interfaz de inicio de sesión | 2 hr | Alta |
| 12 | SP0-12 | Mujica Vallejos Andy Mauricio | Implementar el registro, autenticación e inicio de sesión de usuarios | 5 hr | Alta |
| 13 | SP0-13 | Condori Diaz Marilyn Esther | Realizar pruebas del registro e inicio de sesión | 2 hr | Media |
| 14 | SP0-14 | Delgado Rojas Alberto Caleb | Diseñar la interfaz para la gestión de usuarios, roles y permisos | 4 hr | Alta |
| 15 | SP0-15 | Delgado Rojas Alberto Caleb | Implementar la gestión de usuarios, roles y permisos | 8 hr | Alta |
| 16 | SP0-16 | Delgado Rojas Alberto Caleb | Diseñar la configuración de centros psicológicos bajo arquitectura Multi-Tenant | 4 hr | Alta |
| 17 | SP0-17 | Delgado Rojas Alberto Caleb | Implementar el aislamiento de información de cada centro psicológico mediante Multi-Tenant | 8 hr | Alta |
| 18 | SP0-18 | Velasco Soliz Rolando | Realizar pruebas de usuarios, roles, permisos y aislamiento Multi-Tenant | 4 hr | Alta |
| 19 | SP1-1 | Equipo SCRUM | Diseñar la interfaz para la gestión de psicólogos y sus perfiles profesionales | 4 hr | Alta |
| 20 | SP1-2 | Equipo SCRUM | Implementar la gestión de psicólogos, especialidades, disponibilidad y modalidad de atención | 8 hr | Alta |
| 21 | SP1-3 | Equipo SCRUM | Realizar pruebas de la gestión de psicólogos | 3 hr | Media |
| 22 | SP1-4 | Equipo SCRUM | Diseñar la interfaz para la gestión de pacientes | 4 hr | Alta |
| 23 | SP1-5 | Equipo SCRUM | Implementar el registro, actualización y consulta de pacientes | 8 hr | Alta |
| 24 | SP1-6 | Equipo SCRUM | Realizar pruebas de la gestión de pacientes | 3 hr | Media |
| 25 | SP1-7 | Equipo SCRUM | Diseñar la interfaz del Dashboard administrativo y clínico | 4 hr | Alta |
| 26 | SP1-8 | Equipo SCRUM | Implementar Dashboard con indicadores de citas, pacientes, inasistencias y carga profesional | 8 hr | Alta |
| 27 | SP1-9 | Equipo SCRUM | Realizar pruebas del Dashboard e indicadores principales | 3 hr | Media |
| 28 | SP1-10 | Equipo SCRUM | Diseñar la interfaz para agenda y gestión de citas | 4 hr | Alta |
| 29 | SP1-11 | Equipo SCRUM | Implementar reserva, confirmación, cancelación y reprogramación de citas | 8 hr | Alta |
| 30 | SP1-12 | Equipo SCRUM | Realizar pruebas de agenda y gestión de citas | 3 hr | Media |
| 31 | SP1-13 | Equipo SCRUM | Diseñar la interfaz para sesiones virtuales y videoconferencias | 3 hr | Media |
| 32 | SP1-14 | Equipo SCRUM | Implementar la integración de videoconferencias mediante Jitsi Meet o Zoom | 7 hr | Alta |
| 33 | SP1-15 | Equipo SCRUM | Realizar pruebas de acceso y funcionamiento de las videoconferencias | 3 hr | Media |
| 34 | SP2-1 | Equipo SCRUM | Diseñar la interfaz del formulario previo a la consulta del paciente | 4 hr | Alta |
| 35 | SP2-2 | Equipo SCRUM | Implementar el formulario previo con motivo de consulta, síntomas, urgencia y antecedentes | 8 hr | Alta |
| 36 | SP2-3 | Equipo SCRUM | Realizar pruebas del formulario previo a la consulta | 3 hr | Media |
| 37 | SP2-4 | Equipo SCRUM | Diseñar la interfaz para la historia clínica psicológica | 4 hr | Alta |
| 38 | SP2-5 | Equipo SCRUM | Implementar la gestión de historia clínica psicológica del paciente | 8 hr | Alta |
| 39 | SP2-6 | Equipo SCRUM | Realizar pruebas de la gestión de historia clínica psicológica | 3 hr | Media |
| 40 | SP2-7 | Equipo SCRUM | Diseñar la interfaz para notas de sesión y evolución terapéutica | 4 hr | Alta |
| 41 | SP2-8 | Equipo SCRUM | Implementar el registro de notas, avances, acuerdos, tareas y evolución del paciente | 8 hr | Alta |
| 42 | SP2-9 | Equipo SCRUM | Realizar pruebas del seguimiento y evolución terapéutica | 3 hr | Media |
| 43 | SP2-10 | Equipo SCRUM | Diseñar la interfaz para consentimientos informados y autorizaciones | 3 hr | Alta |
| 44 | SP2-11 | Equipo SCRUM | Implementar la gestión digital de consentimientos informados y permisos | 6 hr | Alta |
| 45 | SP2-12 | Equipo SCRUM | Realizar pruebas de consentimientos y autorizaciones del paciente | 2 hr | Media |
| 46 | SP2-13 | Equipo SCRUM | Implementar el proceso de cierre, pausa y derivación de casos psicológicos | 6 hr | Alta |
| 47 | SP2-14 | Equipo SCRUM | Realizar pruebas del proceso de cierre y derivación de pacientes | 3 hr | Media |
| 48 | SP3-1 | Equipo SCRUM | Diseñar las interfaces de registro e inicio de sesión de la aplicación móvil | 4 hr | Alta |
| 49 | SP3-2 | Equipo SCRUM | Implementar registro e inicio de sesión de pacientes en la aplicación móvil | 7 hr | Alta |
| 50 | SP3-3 | Equipo SCRUM | Realizar pruebas del registro e inicio de sesión móvil | 3 hr | Media |
| 51 | SP3-4 | Equipo SCRUM | Diseñar la interfaz móvil para gestión de citas y notificaciones | 4 hr | Alta |
| 52 | SP3-5 | Equipo SCRUM | Implementar consulta de citas, recordatorios y notificaciones push | 8 hr | Alta |
| 53 | SP3-6 | Equipo SCRUM | Realizar pruebas de citas y notificaciones en la aplicación móvil | 3 hr | Media |
| 54 | SP3-7 | Equipo SCRUM | Diseñar la interfaz móvil para seguimiento, tareas y videoconferencias | 4 hr | Alta |
| 55 | SP3-8 | Equipo SCRUM | Implementar acceso a tareas terapéuticas, seguimiento y teleconsulta desde la aplicación móvil | 8 hr | Alta |
| 56 | SP3-9 | Equipo SCRUM | Realizar pruebas de seguimiento, tareas y videoconferencias en la aplicación móvil | 3 hr | Media |
| 57 | SP3-10 | Equipo SCRUM | Diseñar la interfaz conversacional del chatbot de orientación | 3 hr | Alta |
| 58 | SP3-11 | Equipo SCRUM | Implementar el chatbot para orientación, consultas frecuentes y apoyo en formularios | 8 hr | Alta |
| 59 | SP3-12 | Equipo SCRUM | Realizar pruebas del chatbot con diferentes consultas de pacientes | 3 hr | Media |
| 60 | SP3-13 | Equipo SCRUM | Implementar la clasificación asistida del motivo de consulta y sugerencia de psicólogo | 8 hr | Alta |
| 61 | SP3-14 | Equipo SCRUM | Realizar pruebas de clasificación y asignación asistida por inteligencia artificial | 4 hr | Alta |
| 62 | SP4-1 | Equipo SCRUM | Diseñar las funciones de inteligencia artificial para resúmenes clínicos y alertas de riesgo | 4 hr | Alta |
| 63 | SP4-2 | Equipo SCRUM | Implementar la generación asistida de resúmenes clínicos | 8 hr | Alta |
| 64 | SP4-3 | Equipo SCRUM | Implementar la detección de señales de riesgo y generación de alertas prioritarias | 8 hr | Alta |
| 65 | SP4-4 | Equipo SCRUM | Realizar pruebas de resúmenes, alertas y restricciones de inteligencia artificial | 4 hr | Alta |
| 66 | SP4-5 | Equipo SCRUM | Diseñar la interfaz para reportes administrativos y clínicos | 4 hr | Alta |
| 67 | SP4-6 | Equipo SCRUM | Implementar reportes de citas, pacientes, inasistencias, demanda y carga profesional | 8 hr | Alta |
| 68 | SP4-7 | Equipo SCRUM | Realizar pruebas y exportación de reportes en PDF y Excel | 4 hr | Media |
| 69 | SP4-8 | Equipo SCRUM | Diseñar la interfaz para el control de pagos y estado de cuenta del paciente | 3 hr | Alta |
| 70 | SP4-9 | Equipo SCRUM | Implementar registro de cobros, saldos pendientes y métodos de pago | 7 hr | Alta |
| 71 | SP4-10 | Equipo SCRUM | Realizar pruebas del módulo de control de pagos | 3 hr | Media |
| 72 | SP4-11 | Equipo SCRUM | Implementar y verificar auditoría de accesos, seguridad y trazabilidad de acciones sensibles | 6 hr | Alta |
| 73 | SP4-12 | Equipo SCRUM | Realizar pruebas finales de integración de la plataforma web, aplicación móvil, IA y base de datos | 8 hr | Alta |

## 3.7 Requisitos Funcionales (App web y móvil)

| ID | Funcionalidad | Descripción | Módulo | Plataforma | Prioridad |
|---|---|---|---|---|---|
| RF-01 | Registro y autenticación multi-rol | El sistema debe permitir el registro e inicio de sesión de usuarios con roles diferenciados (Super Admin, Admin de Centro, Psicólogo, Paciente) mediante autenticación segura basada en tokens. | Gestión de Usuarios y Roles | Web / Móvil | Alta |
| RF-02 | Gestión de tenants (centros psicológicos) | Alta, configuración y desactivación de centros psicológicos como entidades independientes dentro de la plataforma SaaS. | Gestión de Usuarios y Roles | Web | Alta |
| RF-03 | Asignación de roles y permisos | El administrador de cada centro puede asignar y modificar roles y permisos a los usuarios de su tenant. | Gestión de Usuarios y Roles | Web | Alta |
| RF-04 | Panel de indicadores administrativos | Métricas operativas del centro en tiempo real. | Dashboard Administrativo | Web | Alta |
| RF-05 | Gestión de configuración del centro | Personalizar parámetros del tenant. | Dashboard Administrativo | Web | Media |
| RF-06 | Registro de pacientes | Alta de pacientes con validación de datos en tiempo real. | Gestión de Pacientes | Web / Móvil | Alta |
| RF-07 | Gestión de perfiles de psicólogos | Especialidad, formación, tarifas, disponibilidad. | Gestión de Psicólogos | Web | Alta |
| RF-08 | Formulario de pre-consulta | Formulario estructurado previo a la primera sesión. | Formularios de Pre-consulta | Web / Móvil | Alta |
| RF-09 | Validación dinámica de formularios | Validación en tiempo real según tipo y obligatoriedad. | Formularios de Pre-consulta | Web / Móvil | Media |
| RF-10 | Clasificación automática de casos (IA) | Clasificar nivel de urgencia y área temática. | Clasificación y Asignación con IA | Web | Alta |
| RF-11 | Asignación sugerida de psicólogo | Sugerencia automática según especialidad, carga y clasificación, con confirmación manual. | Clasificación y Asignación con IA | Web | Alta |
| RF-12 | Chatbot de orientación inicial | Orientación sobre registro, atención y primeros pasos. | Chatbot de Orientación | Web / Móvil | Media |
| RF-13 | Derivación desde el chatbot a soporte humano | Escalar la conversación cuando supere el alcance del bot. | Chatbot de Orientación | Web / Móvil | Media |
| RF-14 | Programación de citas | Agendar verificando disponibilidad en tiempo real. | Agenda y Videoconferencia | Web / Móvil | Alta |
| RF-15 | Modificación y cancelación de citas | Reprogramar/cancelar respetando políticas de anticipación. | Agenda y Videoconferencia | Web / Móvil | Alta |
| RF-16 | Teleconsulta por videollamada | Sesiones de video en tiempo real (WebRTC). | Agenda y Videoconferencia | Web / Móvil | Alta |
| RF-17 | Chat de mensajería durante la sesión | Intercambio de mensajes de texto. | Agenda y Videoconferencia | Web / Móvil | Media |
| RF-18 | Recordatorios automáticos de citas | Notificaciones push/email antes de cada cita. | Agenda y Videoconferencia | Web / Móvil | Alta |
| RF-19 | Registro de estado de ánimo | Escala o emoji diario. | App Móvil del Paciente | Móvil | Alta |
| RF-20 | Ejercicios de mindfulness guiado | Contenido audio/texto. | App Móvil del Paciente | Móvil | Media |
| RF-21 | Gamificación de hábitos saludables | Rachas, puntos, logros. | App Móvil del Paciente | Móvil | Media |
| RF-22 | Historia clínica electrónica | Registro longitudinal, acceso solo autorizado. | Historia Clínica y Seguimiento | Web | Alta |
| RF-23 | Registro de evolución por sesión | Notas de evolución por sesión. | Historia Clínica y Seguimiento | Web | Alta |
| RF-24 | Asignación de tareas terapéuticas | Tareas entre sesiones con fecha límite y objetivo. | Historia Clínica y Seguimiento | Web | Alta |
| RF-25 | Reporte de cumplimiento de tareas | El paciente reporta avance desde la app móvil. | Historia Clínica y Seguimiento | Móvil | Alta |
| RF-26 | Alertas de riesgo clínico | Alertas automáticas al psicólogo. | Alertas y Apoyo a la Decisión | Web | Alta |
| RF-27 | Panel de apoyo a la decisión clínica | Indicadores y tendencias del paciente. | Alertas y Apoyo a la Decisión | Web | Media |
| RF-28 | Gestión de consentimientos y permisos | Registro y almacenamiento de consentimientos. | Permisos y Documentación | Web / Móvil | Alta |
| RF-29 | Control de acceso a documentación clínica | Restricción según rol y relación con el caso. | Permisos y Documentación | Web | Alta |
| RF-30 | Generación de reportes clínicos | Exportar historias clínicas y resúmenes en PDF. | Reportes | Web | Media |
| **RF-31** | **Recuperación de credenciales y contraseña** | **El sistema debe permitir a los usuarios recuperar el acceso a su cuenta mediante el envío de un enlace seguro con token temporal de un solo uso a su correo electrónico registrado.** | **Gestión de Usuarios y Roles** | **Web / Móvil** | **Alta** |

## 3.8 Requisitos no funcionales

| ID | Categoría | Descripción | Prioridad |
|---|---|---|---|
| RNF-01 | Rendimiento | Tiempo de respuesta aceptable de la API bajo carga normal. | Alta |
| RNF-02 | Rendimiento | Calidad de audio/video estable en videoconsultas. | Alta |
| RNF-03 | Escalabilidad | Soportar crecimiento de tenants y usuarios concurrentes. | Alta |
| RNF-04 | Disponibilidad | Operación continua, mínimos tiempos de inactividad. | Alta |
| RNF-05 | Seguridad – Autenticación | Sesiones protegidas, tokens de vida limitada. | Alta |
| RNF-06 | Seguridad – Datos en tránsito | Comunicación cifrada cliente-servidor. | Alta |
| RNF-07 | Seguridad – Datos en reposo | Información clínica protegida contra accesos no autorizados. | Alta |
| RNF-08 | Privacidad y cumplimiento normativo | Manejo de datos de salud según estándares aplicables. | Alta |
| RNF-09 | Aislamiento multi-tenant | Segregación de datos a nivel de infraestructura, no solo de aplicación. | Alta |
| RNF-10 | Control de acceso | Acceso restringido estrictamente según el rol. | Alta |
| RNF-11 | Usabilidad | Interfaz comprensible e intuitiva, incluyendo pacientes vulnerables. | Media |
| RNF-12 | Accesibilidad | Utilizable por personas con discapacidad visual, motriz o cognitiva. | Media |
| RNF-13 | Compatibilidad | Navegadores principales y versiones recientes de móviles. | Media |
| RNF-14 | Mantenibilidad | Código con estándares que faciliten mantenimiento/extensión. | Media |
| RNF-15 | Portabilidad / Despliegue | Despliegue reproducible en distintos entornos. | Alta |
| RNF-16 | Interoperabilidad | Exportación de información clínica en formatos estándar. | Baja |
| RNF-17 | Auditabilidad | Registro inmutable de toda acción crítica. | Alta |
| RNF-18 | Confiabilidad ante fallos | Degradación controlada ante fallos externos (IA, videollamada, notificaciones). | Media |
| RNF-19 | Capacidad de la IA | Resultados consistentes y trazables. | Media |
| RNF-20 | Copias de seguridad | Respaldo periódico de la información. | Alta |

## 3.9 Lista de casos de uso (web y móvil)

| ID | Descripción | Estado | Móvil | Web | Sprint |
|---|---|---|---|---|---|
| CU1 | Gestionar centros psicológicos y configuración Multi-Tenant | Propuesto | | X | SP0 |
| CU2 | Gestionar inicio de sesión y autenticación | Propuesto | X | X | SP0 |
| CU3 | Gestionar usuarios | Propuesto | | X | SP0 |
| CU4 | Gestionar roles y permisos | Propuesto | | X | SP0 |
| CU5 | Gestionar auditoría e historial de accesos | Propuesto | | X | SP4 |
| CU6 | Gestionar psicólogos y perfiles profesionales | Propuesto | | X | SP1 |
| CU7 | Gestionar pacientes | Propuesto | | X | SP1 |
| CU8 | Gestionar disponibilidad y carga de trabajo de psicólogos | Propuesto | | X | SP1 |
| CU9 | Consultar Dashboard e indicadores del centro psicológico | Propuesto | | X | SP1 |
| CU10 | Gestionar alertas de priorización y seguimiento | Propuesto | | X | SP1 |
| CU11 | Gestionar citas y agenda psicológica | Propuesto | X | X | SP1 |
| CU12 | Gestionar recordatorios y notificaciones automáticas | Propuesto | X | X | SP3 |
| CU13 | Gestionar teleconsultas y videoconferencias | Propuesto | X | X | SP1 |
| CU14 | Gestionar formulario previo a la consulta | Propuesto | X | X | SP2 |
| CU15 | Gestionar historia clínica psicológica | Propuesto | | X | SP2 |
| CU16 | Registrar y gestionar notas de sesión | Propuesto | | X | SP2 |
| CU17 | Gestionar evolución, tareas y seguimiento terapéutico | Propuesto | X | X | SP2 |
| CU18 | Gestionar consentimientos informados y autorizaciones | Propuesto | X | X | SP2 |
| CU19 | Gestionar cierre y derivación de casos psicológicos | Propuesto | | X | SP2 |
| CU20 | Interactuar con el chatbot de orientación al paciente | Propuesto | X | X | SP3 |
| CU21 | Clasificar motivo de consulta mediante Inteligencia Artificial | Propuesto | X | X | SP3 |
| CU22 | Sugerir asignación de paciente a psicólogo mediante Inteligencia Artificial | Propuesto | | X | SP3 |
| CU23 | Generar resúmenes clínicos asistidos por Inteligencia Artificial | Propuesto | | X | SP4 |
| CU24 | Detectar señales de riesgo y generar alertas mediante Inteligencia Artificial | Propuesto | | X | SP4 |
| CU25 | Generar y exportar reportes administrativos y clínicos | Propuesto | | X | SP4 |
| CU26 | Gestionar pagos y estado de cuenta del paciente | Propuesto | | X | SP4 |
| **CU27** | **Recuperar contraseña o credenciales de acceso** | Propuesto | **X** | **X** | **SP0** |

> **Cambio respecto a la versión anterior del documento:** CU27 ya NO es "Gestionar inicio de sesión y autenticación en la aplicación móvil" — ahora es **recuperación de contraseña/credenciales**, aplica a Web y Móvil, y se mueve a **Sprint 0**. El registro e inicio de sesión de pacientes en la app móvil sigue existiendo como tarea de backlog (SP3-1/2/3, sección 3.6) y como parte de CU2, pero ya no tiene un CU numerado propio.

## 3.10 Paquetes y casos de Uso

- **Paquete 1 — Administración, Seguridad y Multi-Tenant:** CU1, CU2, CU3, CU4, CU5 y **CU27** (recuperación de contraseña).
- **Paquete 2 — Gestión Clínica y de Profesionales:** CU6, CU7, CU8, CU15, CU16 y CU19.
- **Paquete 3 — Agenda, Comunicación y Seguimiento:** CU9, CU10, CU11, CU12, CU13 y CU17.
- **Paquete 4 — Formularios, Consentimientos y Documentación:** CU14 y CU18.
- **Paquete 5 — Inteligencia Artificial y Chatbot:** CU20, CU21, CU22, CU23 y CU24.
- **Paquete 6 — Reportes y Pagos:** CU25 y CU26.

## 3.11 Planificación Sprint (Diagrama de Gantt)

| ID | Descripción | 25-27 Ago. | 08-10 Sep. | 06-08 Oct. | 03-05 Nov. | 24-26 Nov. | Sprint |
|---|---|---|---|---|---|---|---|
| SP0-1 | Preparación y configuración inicial del proyecto | X | | | | | SP0 |
| SP0-2 | Inicio de sesión y autenticación | X | | | | | SP0 |
| SP0-3 | Gestión de usuarios, roles y permisos | X | | | | | SP0 |
| SP0-4 | Configuración de arquitectura Multi-Tenant | X | | | | | SP0 |
| SP0-5 | Recuperación de contraseña y credenciales de acceso | X | | | | | SP0 |
| SP1-1 | Gestión de psicólogos y perfiles profesionales | | X | | | | SP1 |
| SP1-2 | Gestión de pacientes | | X | | | | SP1 |
| SP1-3 | Gestión de disponibilidad y carga de trabajo | | X | | | | SP1 |
| SP1-4 | Dashboard e indicadores principales | | X | | | | SP1 |
| SP1-5 | Gestión de alertas de priorización | | X | | | | SP1 |
| SP1-6 | Gestión de citas y agenda psicológica | | X | | | | SP1 |
| SP1-7 | Gestión de videoconferencias y teleconsultas | | X | | | | SP1 |
| SP2-1 | Formulario previo a la consulta | | | X | | | SP2 |
| SP2-2 | Gestión de historia clínica psicológica | | | X | | | SP2 |
| SP2-3 | Registro y gestión de notas de sesión | | | X | | | SP2 |
| SP2-4 | Gestión de evolución y seguimiento terapéutico | | | X | | | SP2 |
| SP2-5 | Gestión de tareas y acuerdos terapéuticos | | | X | | | SP2 |
| SP2-6 | Gestión de consentimientos informados y autorizaciones | | | X | | | SP2 |
| SP2-7 | Gestión de cierre y derivación de casos | | | X | | | SP2 |
| SP3-1 | Registro e inicio de sesión en la aplicación móvil | | | | X | | SP3 |
| SP3-2 | Gestión de citas desde la aplicación móvil | | | | X | | SP3 |
| SP3-3 | Gestión de notificaciones y recordatorios | | | | X | | SP3 |
| SP3-4 | Seguimiento y tareas terapéuticas desde la aplicación móvil | | | | X | | SP3 |
| SP3-5 | Interacción con el chatbot de orientación | | | | X | | SP3 |
| SP3-6 | Clasificación del motivo de consulta mediante IA | | | | X | | SP3 |
| SP3-7 | Sugerencia de asignación de psicólogo mediante IA | | | | X | | SP3 |
| SP4-1 | Generación asistida de resúmenes clínicos | | | | | X | SP4 |
| SP4-2 | Detección de señales de riesgo y alertas prioritarias | | | | | X | SP4 |
| SP4-3 | Generación de reportes administrativos y clínicos | | | | | X | SP4 |
| SP4-4 | Exportación de reportes en PDF y Excel | | | | | X | SP4 |
| SP4-5 | Gestión de pagos y estado de cuenta | | | | | X | SP4 |
| SP4-6 | Auditoría, seguridad e historial de accesos | | | | | X | SP4 |
| SP4-7 | Pruebas finales e integración de la plataforma | | | | | X | SP4 |

---

# CAPÍTULO 4 – DESARROLLO SPRINT 0

> Este capítulo documenta el desarrollo del Sprint 0 siguiendo la estructura de SCRUM: planificación, historias de usuario detalladas (Tarjetas 3C), proceso de desarrollo, seguimiento diario, revisión, retrospectiva y artefactos de medición.
>
> **Nota de uso:** el contenido de este capítulo (Daily Scrum día por día, burndown/burnup, taskboard) es la **narrativa del informe académico** — describe cómo se documenta el Sprint 0 para la entrega escrita. No es literal para el código: los nombres de endpoint mencionados aquí (`/api/auth/login/`, etc.) son ilustrativos del diseño conceptual, no tienen que coincidir carácter por carácter con las rutas reales del backend (que usa `/api/users/auth/login/`, `/api/users/me/`, etc.) — lo que importa es que la funcionalidad descrita exista.

## 4.1 Sprint Planning

### 4.1.1 Objetivos del Sprint 0

- Entorno de desarrollo configurado y funcional para backend (Django/DRF), frontend web (Angular), aplicación móvil (Flutter) y base de datos (PostgreSQL).
- Módulo de registro, autenticación, inicio de sesión y **recuperación de contraseña** implementado y probado.
- Módulo de gestión de usuarios, roles y permisos implementado y probado.
- Arquitectura Multi-Tenant configurada con aislamiento de datos entre centros.
- Prototipos iniciales de las interfaces principales diseñados en Figma.
- Documentación del proyecto completada.

**Duración del Sprint:** 1 semana (18 al 24 de agosto de 2026)
**Fecha de presentación:** 25 y 27 de agosto de 2026
**Casos de uso involucrados:** CU1, CU2, CU3, CU4, CU27
**Requisitos funcionales asociados:** RF-01, RF-02, RF-03, RF-31

### 4.1.2 Historias de Usuario del Sprint 0

Modelo de las 3C (Ron Jeffries): **Tarjeta** (Como [rol], quiero [acción], para [beneficio]), **Conversación** (diálogo de refinamiento entre PO/SM/equipo), **Confirmación** (criterios de aceptación en formato BDD "Dado que... cuando... entonces...").

**Estimación:** Planning Poker con secuencia de Fibonacci (1, 2, 3, 5, 8, 13, 21).

**Resumen de Historias de Usuario del Sprint 0**

| ID | Título | Prioridad | PHU | Desarrollador a cargo | Prototipo Asociado |
|---|---|---|---|---|---|
| HU-01 | Registro de SuperAdministrador | Alta | 3 | Mujica Vallejos Andy Mauricio | Pantalla Registro SuperAdmin (Figma) |
| HU-02 | Inicio de sesión multi-rol | Alta | 5 | Mujica Vallejos Andy Mauricio | Pantalla Login Multi-Rol (Figma) |
| HU-03 | Alta de centros psicológicos | Alta | 8 | Delgado Rojas Alberto Caleb | Pantalla Alta de Centro / Tenant (Figma) |
| HU-04 | Configuración del centro | Media | 5 | Delgado Rojas Alberto Caleb | Pantalla Configuración Institucional (Figma) |
| HU-05 | Registro de usuarios del centro | Alta | 5 | Delgado Rojas Alberto Caleb | Pantalla Gestión de Usuarios (Figma) |
| HU-06 | Asignación de roles y permisos | Alta | 8 | Delgado Rojas Alberto Caleb | Pantalla Asignación de Roles/Permisos (Figma) |
| HU-07 | Aislamiento Multi-Tenant | Alta | 13 | Delgado Rojas Alberto Caleb | Vista de Aislamiento de Datos por Tenant (Figma) |
| HU-08 | Gestión de centros suscritos | Media | 5 | Delgado Rojas Alberto Caleb | Pantalla Listado y Edición de Centros (Figma) |
| HU-09 | Cierre de sesión seguro | Media | 2 | Mujica Vallejos Andy Mauricio | Modal de Cierre de Sesión (Figma) |
| HU-10 | Recuperación de contraseña | Media | 3 | Mujica Vallejos Andy Mauricio | Pantalla Recuperación Contraseña (Figma) |

**Detalle de Historias de Usuario y Criterios de Aceptación (Tarjetas 3C)**

**HU-01 — Registro de SuperAdministrador** (Prioridad: Alta · PHU: 3 · Desarrollador: Mujica Vallejos Andy Mauricio)

Descripción: Como SuperAdministrador, quiero registrarme con credenciales seguras, para acceder al panel de administración global del sistema.

Criterios de aceptación:
a) Dado que no existe un SuperAdministrador registrado, cuando ingreso un correo válido y una contraseña segura (mínimo 8 caracteres, una mayúscula, un número y un carácter especial), entonces el sistema crea mi cuenta y me redirige al panel de administración.
b) Dado que ya existe un SuperAdministrador registrado con el mismo correo, cuando intento registrarme, entonces el sistema muestra un mensaje de error indicando que el correo ya está en uso.
c) Dado que ingreso una contraseña que no cumple los requisitos de seguridad, cuando envío el formulario, entonces el sistema muestra los requisitos mínimos que faltan por cumplir.

**HU-02 — Inicio de sesión multi-rol** (Alta · PHU: 5 · Mujica Vallejos Andy Mauricio)

Descripción: Como usuario del sistema, quiero iniciar sesión con mi correo y contraseña mediante tokens, para acceder a las funcionalidades de mi rol.

Criterios de aceptación:
a) Dado que tengo una cuenta activa, cuando ingreso mi correo y contraseña correctos, entonces el sistema genera un token JWT, inicia mi sesión y me redirige al panel correspondiente a mi rol.
b) Dado que ingreso credenciales incorrectas, cuando envío el formulario de login, entonces el sistema muestra un mensaje de error sin revelar si el correo existe o no.
c) Dado que mi cuenta está desactivada o suspendida, cuando intento iniciar sesión, entonces el sistema muestra un mensaje indicando que mi cuenta no está disponible.

**HU-03 — Alta de centros psicológicos** (Alta · PHU: 8 · Delgado Rojas Alberto Caleb)

Descripción: Como SuperAdministrador, quiero dar de alta un nuevo centro psicológico, para que opere con datos aislados dentro de la plataforma.

Criterios de aceptación:
a) Dado que soy SuperAdministrador autenticado, cuando completo el formulario de alta con nombre del centro, dirección, teléfono y correo de contacto, entonces el sistema crea un nuevo tenant con su esquema de base de datos aislado.
b) Dado que ya existe un centro con el mismo nombre, cuando intento dar de alta otro centro con ese nombre, entonces el sistema muestra un mensaje indicando que el nombre ya está en uso.
c) Dado que se crea un centro exitosamente, cuando verifico la base de datos, entonces el nuevo centro tiene su propio esquema PostgreSQL con las tablas necesarias.

**HU-04 — Configuración del centro** (Media · PHU: 5 · Delgado Rojas Alberto Caleb)

Descripción: Como Administrador del Centro, quiero configurar los datos institucionales de mi centro, para personalizar el funcionamiento de la plataforma según mis necesidades.

Criterios de aceptación:
a) Dado que soy Administrador del Centro autenticado, cuando accedo a la sección de configuración, entonces puedo editar nombre, dirección, teléfono, correo, horarios de atención y logo del centro.
b) Dado que modifico los datos del centro, cuando guardo los cambios, entonces el sistema actualiza la información y muestra un mensaje de confirmación.
c) Dado que accedo a la configuración, cuando los cambios se guardan, entonces solo afectan a mi centro y no a otros centros de la plataforma.

**HU-05 — Registro de usuarios del centro** (Alta · PHU: 5 · Delgado Rojas Alberto Caleb)

Descripción: Como Administrador del Centro, quiero registrar usuarios dentro de mi centro, para que accedan al sistema según el rol que les asigne.

Criterios de aceptación:
a) Dado que soy Administrador del Centro autenticado, cuando registro un nuevo usuario con nombre, correo y rol, entonces el sistema crea la cuenta dentro del tenant de mi centro.
b) Dado que intento registrar un usuario con un correo ya existente en mi centro, cuando envío el formulario, entonces el sistema muestra un mensaje de error indicando que el correo ya está registrado.
c) Dado que registro un usuario exitosamente, cuando el usuario inicia sesión, entonces solo puede ver y acceder a los datos de mi centro.

**HU-06 — Asignación de roles y permisos** (Alta · PHU: 8 · Delgado Rojas Alberto Caleb)

Descripción: Como Administrador del Centro, quiero asignar roles y permisos a los usuarios de mi centro, para controlar el acceso de cada persona a las funcionalidades del sistema.

Criterios de aceptación:
a) Dado que soy Administrador del Centro autenticado, cuando selecciono un usuario y le asigno el rol de Psicólogo, entonces ese usuario puede acceder a las funcionalidades clínicas pero no a las administrativas.
b) Dado que cambio el rol de un usuario de Recepcionista a Coordinador Clínico, cuando el usuario inicia sesión nuevamente, entonces ve las opciones correspondientes al nuevo rol.
c) Dado que un usuario tiene rol de Psicólogo, cuando intenta acceder a funcionalidades de Administrador, entonces el sistema le deniega el acceso y muestra un mensaje de autorización insuficiente.

**HU-07 — Aislamiento Multi-Tenant** (Alta · PHU: 13 · Delgado Rojas Alberto Caleb)

Descripción: Como Administrador del Centro, quiero que la información de mi centro esté completamente aislada de otros centros, para garantizar la confidencialidad de los datos.

Criterios de aceptación:
a) Dado que existen dos centros registrados (Centro A y Centro B), cuando el Administrador del Centro A consulta la lista de pacientes, entonces solo ve los pacientes de su centro y ninguno del Centro B.
b) Dado que un usuario del Centro A intenta acceder a una URL correspondiente al Centro B, cuando el sistema procesa la solicitud, entonces deniega el acceso y muestra un error de autorización.
c) Dado que el SuperAdministrador consulta la base de datos, cuando revisa los esquemas, entonces cada centro tiene su propio esquema PostgreSQL con datos completamente separados.

**HU-08 — Gestión de centros suscritos** (Media · PHU: 5 · Delgado Rojas Alberto Caleb)

Descripción: Como SuperAdministrador, quiero editar, suspender o dar de baja centros psicológicos suscritos, para mantener el control y la administración de la plataforma.

Criterios de aceptación:
a) Dado que soy SuperAdministrador autenticado, cuando edito los datos de un centro suscrito, entonces los cambios se reflejan inmediatamente en la plataforma.
b) Dado que suspendo un centro, cuando los usuarios de ese centro intentan iniciar sesión, entonces el sistema les muestra un mensaje indicando que su centro está temporalmente suspendido.
c) Dado que doy de baja un centro, cuando consulto la lista de centros activos, entonces ese centro ya no aparece en la lista y sus usuarios no pueden acceder.

**HU-09 — Cierre de sesión seguro** (Media · PHU: 2 · Mujica Vallejos Andy Mauricio)

Descripción: Como usuario del sistema, quiero cerrar mi sesión de manera segura, para proteger mi cuenta cuando deje de usar la plataforma.

Criterios de aceptación:
a) Dado que tengo una sesión activa, cuando presiono el botón de cerrar sesión, entonces el sistema invalida mi token JWT y me redirige a la pantalla de inicio de sesión.
b) Dado que cerré mi sesión, cuando intento acceder a una funcionalidad protegida sin volver a iniciar sesión, entonces el sistema me redirige al formulario de login.

**HU-10 — Recuperación de contraseña y credenciales** (Media · PHU: 3 · Mujica Vallejos Andy Mauricio)

Caso de uso asociado: **CU27** (Recuperar contraseña o credenciales de acceso) · Requisito funcional asociado: **RF-31**

Descripción: Como usuario del sistema, quiero recuperar mi contraseña mediante correo electrónico, para acceder nuevamente a la plataforma en caso de olvidar o bloquear mis credenciales de acceso.

Criterios de aceptación:
a) Dado que olvidé mi contraseña, cuando ingreso mi correo registrado y solicito la recuperación, entonces el sistema envía un correo con un enlace seguro de restablecimiento con token temporal válido por 30 minutos.
b) Dado que recibí el correo de recuperación, cuando accedo al enlace dentro del tiempo de validez, entonces puedo establecer una nueva contraseña que cumpla los requisitos de seguridad.
c) Dado que el enlace de recuperación ha expirado o ya fue utilizado, cuando intento acceder nuevamente con ese enlace, entonces el sistema me indica que el token ya no es válido y debo solicitar uno nuevo.

### 4.1.3 Contexto del Sistema

**Actores:** SuperAdministrador, Administrador del Centro, Usuario (todos los roles: inicia sesión, cierra sesión, recupera contraseña).

**Diagrama de Clases del Sprint 0 (conceptual):**
- Tenant: id, nombre, slug, esquema, activo, fecha_creacion, fecha_actualizacion
- Usuario: id, email, password_hash, nombre, apellido, telefono, tenant_id, rol_id, activo, fecha_creacion
- Rol: id, nombre, descripcion, tenant_id
- Permiso: id, nombre, codigo, descripcion
- RolPermiso: id, rol_id, permiso_id
- Centro: id, nombre, direccion, telefono, email, logo, configuracion, tenant_id
- TokenAcceso: id, usuario_id, token, fecha_expiracion, activo

**Flujo de autenticación:** login → validación de credenciales → verificación de cuenta activa → identificación de tenant → generación de JWT (usuario, rol, tenant) → redirección por rol.

**Flujo de aislamiento Multi-Tenant:** solicitud HTTP → middleware de tenant identifica esquema por subdominio/header → consulta ejecutada en el esquema aislado → retorno de datos exclusivos del tenant → error si el tenant no existe o está suspendido.

### 4.1.4 Sprint Backlog

18 tareas del Product Backlog (SP0-1 a SP0-18), todas marcadas **Terminado** al cierre del Sprint 0. Total: **76 horas estimadas**.

### 4.1.5 Equipo SCRUM del Sprint 0

| Nombre | Rol SCRUM | Tareas asignadas |
|---|---|---|
| Condori Diaz Marilyn Esther | Product Owner | SP0-1 a SP0-9 (equipo), SP0-13 |
| Delgado Rojas Alberto Caleb | Scrum Master | SP0-1 a SP0-9 (equipo), SP0-14, SP0-15, SP0-16, SP0-17 |
| Mujica Vallejos Andy Mauricio | Development Team | SP0-1 a SP0-9 (equipo), SP0-10, SP0-11, SP0-12 |
| Velasco Soliz Rolando | Development Team | SP0-1 a SP0-9 (equipo), SP0-18 |
| Larrazabal Rojas Julio Cesar | Development Team | SP0-1 a SP0-9 (equipo) |
| Romero Saavedra Maria Ilse | Development Team | SP0-1 a SP0-9 (equipo) |

## 4.2 Proceso de Desarrollo por Historia de Usuario

### 4.2.1 Diseño

**Arquitectura (tres capas, Multi-Tenant):**
- **Presentación:** Web (Angular 17 + TypeScript), Móvil (Flutter 3.x + Dart), comunicación vía API REST con interceptores JWT.
- **Lógica de negocio:** Django 5.x + DRF, JWT (djangorestframework-simplejwt), `django-tenants` para esquemas PostgreSQL, permisos RBAC. Apps Django del Sprint 0 (conceptuales en el documento): `core`, `accounts`, `tenants` — en el código real del proyecto, la organización equivalente es `apps.tenants` y `apps.users`.
- **Datos:** PostgreSQL 16, aislamiento por esquema (público para datos compartidos, uno por centro para datos aislados), Django ORM con migraciones por esquema.

**Diseño de Datos (esquema conceptual):**
- Esquema público: `tenants_tenant`, `tenants_dominio`, `accounts_superadmin`.
- Esquema por tenant: `accounts_usuario`, `accounts_rol`, `accounts_permiso`, `accounts_rol_permiso`, `core_centro`, `accounts_token_recuperacion`.

**Flujos de lógica de negocio:**
1. Registro/Login (HU-01, HU-02), Logout (HU-09), Recuperación (HU-10: token temporal, correo con enlace, nueva contraseña dentro del período de validez).
2. Gestión de Usuarios/Roles/Permisos (HU-05, HU-06): CRUD de usuarios por tenant, asignación de rol, verificación de permisos por middleware.
3. Gestión Multi-Tenant (HU-03, HU-04, HU-07, HU-08): alta de centro → creación de esquema → migraciones automáticas → Admin de Centro por defecto → middleware de tenant en cada solicitud.

### 4.2.2 Implementación

**Componentes conceptuales descritos en el informe** (nombres de referencia del documento; en el código real del proyecto la implementación equivalente vive en `apps.tenants` y `apps.users`, con endpoints bajo `/api/users/...`):

| Endpoint (documento) | Descripción | Equivalente real implementado |
|---|---|---|
| POST /api/auth/register/ | Registro de usuario | POST /api/users/auth/register/ |
| POST /api/auth/login/ | Login (JWT) | POST /api/users/auth/login/ |
| POST /api/auth/logout/ | Logout (invalida JWT) | Logout es local (limpieza de token en el cliente); no hay blacklist de tokens en el servidor |
| POST /api/auth/password-reset/ | Solicitud de recuperación | *(pendiente de implementar — ver abajo)* |
| POST /api/auth/password-reset-confirm/ | Confirmación de nueva contraseña | *(pendiente de implementar — ver abajo)* |
| GET/POST /api/users/ | Listar/crear usuarios | Pendiente (fuera del alcance de CU27) |
| GET /api/users/{id}/ | Detalle de usuario | GET /api/users/me/ (perfil propio) |
| GET/POST /api/roles/, /api/tenants/, /api/centro/config/ | Roles, tenants, configuración | Pendiente (HU-03 a HU-08, fuera del alcance de CU27) |

**Frontend Web (Angular):** LoginComponent, RegisterComponent, PasswordResetComponent, DashboardComponent, UserListComponent, UserFormComponent, RoleListComponent, RoleFormComponent, TenantListComponent, TenantFormComponent, CentroConfigComponent, AuthService, AuthGuard, AuthInterceptor.

### 4.2.3 Pruebas

25 pruebas de aceptación (TP-01 a TP-25) mapeadas a HU-01…HU-10, **25 aprobadas, 0 fallidas** según el informe. Incluye TP-23/24/25 para recuperación de contraseña (correo enviado, restablecimiento exitoso, enlace expirado detectado).

## 4.3 Daily Scrum

Registro diario del Sprint 0 (18 al 24 de agosto de 2026), 7 días de reuniones de 15 minutos. Impedimentos notables: instalación/configuración de PostgreSQL, configuración inicial de `django-tenants`, ajuste de serializers para validaciones de roles y permisos.

## 4.4 Sprint Review

Todos los objetivos del Sprint 0 fueron cumplidos satisfactoriamente. Retroalimentación destacada: agregar validación visual de fortaleza de contraseña en el frontend; documentar relaciones en diagrama ER formal; listar permisos predefinidos por rol; aislamiento Multi-Tenant verificado correctamente entre dos centros de prueba.

## 4.5 Sprint Retrospective

**Qué salió bien:** entorno de desarrollo sin problemas mayores, comunicación efectiva, Multi-Tenant funcional desde el inicio, 25/25 pruebas aprobadas, documentación a tiempo, prototipos en Figma útiles.

**Qué no salió bien:** instalación de PostgreSQL tomó más tiempo del estimado, configuración de `django-tenants` requirió investigación adicional, distribución de tareas de equipo mejorable, estimaciones optimistas en tareas de implementación.

**Mejoras para el Sprint 1:** margen para imprevistos técnicos, distribución más equitativa de tareas individuales, documentar problemas técnicos y soluciones, pruebas unitarias desde el inicio, canal de comunicación para impedimentos fuera de las daily.

## 4.6 Burndown y Burnup

Total: 76 horas estimadas, ejecutadas en 7 días, con avance real ligeramente por debajo del ideal en los días 1-2 (investigación/alineación) y aceleración a partir del día 3. Cierre en el día 7 con 100% de horas ejecutadas y 18/18 tareas completadas.

## 4.7 Gráfica de Esfuerzo y Datos de Esfuerzo

**Total horas estimadas:** 76 · **Total horas reales:** 87 · **Desviación:** +11 horas (+14.5%)

Mayor desviación en tareas de desarrollo individual (modelado BD, implementar auth, implementar usuarios/roles, implementar Multi-Tenant: +6h en conjunto), por configuración de esquemas aislados con `django-tenants` e integración de validaciones en serializers. Recomendación para Sprint 1: incorporar holgura del 15% en estimaciones de lógica de negocio y base de datos.

## 4.8 Scrum Taskboard

Estado final al cierre del Sprint 0: **18/18 tareas en "Terminado" (100%)**, 0 en "Por hacer", 0 en "En progreso". Incremento de software: módulo de autenticación JWT, gestión de usuarios/roles/permisos y arquitectura Multi-Tenant con esquemas PostgreSQL completamente operativa y verificada.

---

# BIBLIOGRAFÍA

## a. Libros y Literatura

- American Psychological Association. (2017). *Ethical principles of psychologists and code of conduct.* APA.
- Beck, J. S. (2011). *Cognitive behavior therapy: Basics and beyond* (2.ª ed.). Guilford Press.
- Colegio de Psicólogos de Bolivia. (2002). *Código de ética del psicólogo boliviano.* La Paz, Bolivia.
- Fernández-Ballesteros, R. (2013). *Evaluación psicológica: Conceptos, métodos y estudio de casos* (2.ª ed.). Ediciones Pirámide.
- Graham, S., Depp, C., Lee, E. E., Nebeker, C., Tu, X., Kim, H. C., & Jeste, D. V. (2019). Artificial intelligence for mental health and mental illnesses: An overview. *Current Psychiatry Reports, 21*(11), 1-15.
- Laudon, K. C., & Laudon, J. P. (2020). *Management information systems: Managing the digital firm* (16.ª ed.). Pearson.
- Organización Mundial de la Salud. (2022). *Informe mundial sobre salud mental: Transformar la salud mental para todos.* OMS.
- Pressman, R. S., & Maxim, B. R. (2020). *Ingeniería del software: Un enfoque práctico* (9.ª ed.). McGraw-Hill.
- Schwaber, K., & Sutherland, J. (2020). *La Guía de Scrum.* Scrum.org.
- Sommerville, I. (2016). *Software engineering* (10.ª ed.). Pearson.

## b. Sitios Web Especializados

Angular, Django, Flutter (documentación oficial); MentalGest; PostgreSQL; SimplePractice; Spring Health; Talkspace; TherapyNotes; iClinic; Psicología.io; OMS.

## c. Personas (Entrevistas y Casos de Estudio)

- Lic. Marilyn Esther Condori Diaz (Product Owner del Proyecto): entrevista del 18 de agosto de 2026 sobre alcance funcional, historia clínica psicológica y prioridades del Product Backlog.
- Lic. Claudia Mendoza V. (Psicóloga Clínica): entrevista semiestructurada sobre flujos de atención, notas de sesión, consentimientos informados y telepsicología en Bolivia.
- Dr. Fernando Ramos G. (Coordinador de Centro Psicológico Universitario): requerimientos de gestión multi-rol, asignación de pacientes a terapeutas en formación, reportes administrativos y de supervisión clínica.

---

# ANEXOS

**Anexo A:** Caso de Estudio 1 — MentalGest (agenda médica, expediente clínico digital, notas de sesión, consentimientos, facturación, reportes).

**Anexo B:** Caso de Estudio 2 — Talkspace (mensajería/audio/video síncrono y asíncrono, evaluación inicial, asignación inteligente de terapeutas).

**Anexo C:** Caso de Estudio 3 — Spring Health ("Precision Mental Healthcare", cuestionarios validados clínicamente, ML para predicción de tratamiento y triage temprano).

**Anexo D:** Prototipos de Interfaces de Usuario en Figma (Sprint 0): Registro de SuperAdministrador (HU-01), Inicio de Sesión Multi-Rol (HU-02), Alta y Gestión de Centros (HU-03/HU-08), Configuración Institucional (HU-04), Gestión de Usuarios y Roles (HU-05/HU-06), Recuperación de Contraseña (HU-10).
