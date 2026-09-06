# UNIVERSIDAD AUTÓNOMA GABRIEL RENÉ MORENO
## FACULTAD DE INGENIERÍA EN CIENCIAS DE LA COMPUTACIÓN Y TELECOMUNICACIONES
### CARRERA DE INGENIERÍA EN SISTEMAS / INFORMÁTICA

---

# INF-412: PRUEBAS DE SOFTWARE
**Docente:** M.Sc. Angélica Garzón  
**Materia:** Sistemas de Información II / Pruebas de Software (INF-412)  
**Proyecto:** Plataforma Web y Móvil de Gestión Integral de Salud Mental (SIGEPSI)  
**Grupo:** # 9  

### Integrantes del Equipo SCRUM:
| Integrante | Registro | Rol en el Proyecto |
|---|---|---|
| **Condori Diaz Marilyn Esther** | 224051237 | Product Owner |
| **Delgado Rojas Alberto Caleb** | 224027204 | Scrum Master |
| **Mujica Vallejos Andy Mauricio** | 224028367 | Development Team |
| **Velasco Soliz Rolando** | 223044768 | Development Team |
| **Larrazabal Rojas Julio Cesar** | 223049255 | Development Team |
| **Romero Saavedra Maria Ilse** | 222009772 | Development Team |

---

# DOCUMENTO DE PRUEBAS FUNCIONALES Y DE CAJA NEGRA — SPRINT 1 (SP1)

---

## 1. FUNDAMENTACIÓN TEÓRICA DE PRUEBAS FUNCIONALES Y DE CAJA NEGRA

### 1.1 ¿Qué son las pruebas funcionales?
Son un tipo de pruebas de software que se enfocan en verificar **qué hace el sistema**, no cómo está hecho internamente.  
Evalúan las funciones del software comparándolas con los requisitos, casos de uso y expectativas del usuario final.

### 1.2 Definición de pruebas de caja negra
Las pruebas de caja negra (*Black Box Testing*) son un método donde el evaluador no conoce la estructura interna del código fuente.  
El foco está estrictamente en:
* **Entradas:** Datos provistos por el usuario o interfaces externas.
* **Procesos esperados:** Comportamiento y lógica visible de negocio.
* **Salidas correctas:** Respuestas, persistencia de datos, cambios de estado y mensajes del sistema.

Se usa para validar comportamiento y cumplimiento de requisitos, no lógica interna de código.

### 1.3 Técnicas de caja negra aplicadas en el Sprint 1
| Técnica | Explicación | Aplicación en SP1 (SIGEPSI) |
|---|---|---|
| **Partición de equivalencia** | Agrupa entradas en clases válidas e inválidas para probar solo representantes. | Validación de formatos de correo electrónico, números telefónicos de contacto y documentos de identidad de pacientes. |
| **Valores límite (Boundary Value)** | Revisa los límites donde suelen ocurrir errores: mínimo, máximo, dentro y fuera del rango. | Horarios de atención (08:00 a 20:00), duración de citas (45, 50, 60, 90 minutos) y longitud mínima de campos obligatorios. |
| **Tablas de decisión** | Se usa cuando hay reglas complejas. Se verifican combinaciones de condiciones. | Disponibilidad del psicólogo combinada con el horario solicitado y el estado del paciente (activo/suspendido). |
| **Transición de estados** | Se prueba cómo responde el sistema cuando cambia de estado por acciones del usuario. | Ciclo de vida de una cita: `Reservada` $\rightarrow$ `Confirmada` $\rightarrow$ `Reprogramada` / `Cancelada` $\rightarrow$ `En teleconsulta` $\rightarrow$ `Finalizada`. |

---

## 2. HISTORIAS DE USUARIO (HU) SCRUM CON CRITERIOS Y PRUEBAS CAJA NEGRA (SPRINT 1)

> Formato oficial según las diapositivas académicas de INF-412 (Páginas 5, 6 y 7 de la guía metodológica).

---

### HU 1 – Directorio y Registro de Psicólogos (CU6)

#### Historia de Usuario:
**Como** Administrador del Centro Psicológico  
**quiero** registrar y administrar a los profesionales psicólogos con sus especialidades y modalidad de atención  
**para** mantener habilitado el equipo terapéutico que brindará atención clínica en la institución.

#### Descripción:
Permite dar de alta a nuevos terapeutas dentro del tenant del centro, asignando credenciales de acceso, datos de contacto, modalidad de atención (Presencial, Virtual o Mixta) y vinculación con sus especialidades clínicas (Psicología Clínica, Infantil, Cognitivo-Conductual, etc.).

#### Criterios de aceptación:
1. El sistema debe permitir registrar un nuevo psicólogo ingresando nombre, apellido, correo electrónico único, contraseña inicial y modalidad de atención.
2. Si el correo electrónico ya está registrado en el sistema, debe mostrar el mensaje: *"Este correo electrónico ya se encuentra registrado"*.
3. Si los campos obligatorios (nombre, apellido, correo, contraseña) están vacíos, no debe permitir el registro y debe mostrar *"Todos los campos marcados con asterisco son obligatorios"*.
4. Si la contraseña no cumple las políticas mínimas de seguridad (al menos 8 caracteres), debe mostrar *"La contraseña debe tener al menos 8 caracteres"*.
5. Debe permitir asociar una o múltiples especialidades activas y definir la modalidad de atención.

#### Casos de prueba funcionales (Caja negra):
| ID | Entrada | Proceso | Salida esperada |
|---|---|---|---|
| **CP01** | Nombre: "Carlos", Apellido: "Mendoza", Correo: "cmendoza@centro.com", Password: "Password123!", Modalidad: "Mixta", Especialidad: "Clínica" | Intentar registro | Psicólogo creado exitosamente, se agrega a la lista visible con estado Activo |
| **CP02** | Correo ya existente: "cmendoza@centro.com" con demás datos válidos | Intentar registro | Mensaje de error: *"Este correo electrónico ya se encuentra registrado"* |
| **CP03** | Campos obligatorios vacíos (Nombre="", Correo="") | Intentar registro | Formulario bloqueado con mensaje: *"Todos los campos marcados con asterisco son obligatorios"* |
| **CP04** | Contraseña corta: "123" | Intentar registro | Mensaje de alerta: *"La contraseña debe tener al menos 8 caracteres"* |
| **CP05** | Búsqueda por texto: "Carlos" en la barra de filtro | Filtrar directorio | Lista filtrada mostrando únicamente los terapeutas cuyo nombre coincide |

**Adjunto:** Interfaz `psicologo-list.component.html` (Directorio de Psicólogos y modal *"Registrar Psicólogo"*).

---

### HU 2 – Horarios y Disponibilidad Semanal de Psicólogos (CU8)

#### Historia de Usuario:
**Como** Psicólogo o Coordinador Clínico  
**quiero** definir y actualizar mis franjas horarias de disponibilidad semanal  
**para** que los pacientes y recepcionistas conozcan los turnos habilitados para agendar citas sin generar conflictos.

#### Descripción:
Permite a cada psicólogo registrar sus horarios de atención por día de la semana (Lunes a Domingo), estableciendo una hora de inicio y una hora de fin para cada franja de disponibilidad.

#### Criterios de aceptación:
1. El sistema debe permitir añadir una franja horaria seleccionando un día de la semana (Lunes a Domingo), hora de inicio y hora de fin válidas.
2. La hora de fin debe ser estrictamente posterior a la hora de inicio; de lo contrario, debe mostrar *"La hora de fin debe ser posterior a la hora de inicio"*.
3. No se permite registrar una franja que se solape o choque con un horario ya registrado para el mismo día; debe mostrar *"La franja horaria entra en conflicto con un horario ya existente"*.
4. Si falta seleccionar el día o las horas, debe mostrar *"Debe completar día, hora de inicio y hora de fin"*.
5. Debe permitir eliminar una franja horaria existente actualizando inmediatamente la vista.

#### Casos de prueba funcionales (Caja negra):
| ID | Entrada | Acción | Salida esperada |
|---|---|---|---|
| **CP01** | Día: Lunes, Inicio: 08:00, Fin: 12:00 | Agregar franja | Franja agregada con éxito; se visualiza en la lista de turnos del psicólogo |
| **CP02** | Día: Lunes, Inicio: 14:00, Fin: 13:00 (Fin menor a Inicio) | Agregar franja | Error: *"La hora de fin debe ser posterior a la hora de inicio"* |
| **CP03** | Día: Lunes, Inicio: 10:00, Fin: 11:30 (Solapada con franja 08:00-12:00) | Agregar franja | Error: *"La franja horaria entra en conflicto con un horario ya existente"* |
| **CP04** | Día: Martes, Inicio="", Fin="" | Agregar franja | Error: *"Debe completar día, hora de inicio y hora de fin"* |
| **CP05** | Clic en botón "Eliminar" de franja Lunes 08:00-12:00 | Eliminar franja | La franja se elimina de la base de datos y desaparece de la tabla |

**Adjunto:** Interfaz `psicologo-list.component.html` (Modal *"Horarios y Disponibilidad Semanal (CU8)"*).

---

### HU 3 – Registro y Directorio de Pacientes (CU7)

#### Historia de Usuario:
**Como** Recepcionista del Centro  
**quiero** registrar los datos personales y de contacto de un nuevo paciente  
**para** aperturar su expediente clínico y habilitar su atención dentro del sistema.

#### Descripción:
Permite la creación de la ficha básica de un paciente con documento de identidad, nombres, apellidos, correo, teléfono, fecha de nacimiento, género, dirección y contacto de emergencia, validando la unicidad del documento en el centro.

#### Criterios de aceptación:
1. El sistema debe permitir registrar un paciente con nombre, apellido, correo válido y documento de identidad.
2. Si el número de documento de identidad o correo ya existe en el centro, debe mostrar: *"El documento de identidad o correo ya pertenece a un paciente registrado"*.
3. Los campos nombre, apellido y correo deben ser de ingreso obligatorio.
4. Debe permitir buscar y filtrar pacientes en tiempo real por nombre, documento de identidad o correo.

#### Casos de prueba funcionales (Caja negra):
| ID | Entrada | Proceso | Salida esperada |
|---|---|---|---|
| **CP01** | Nombre: "Ana", Apellido: "Torres", CI: "8934521", Correo: "ana.torres@gmail.com", Tel: "76543210" | Intentar registro | Paciente registrado satisfactoriamente y mostrado en la primera fila de la tabla |
| **CP02** | CI duplicado: "8934521" con otros nombres | Intentar registro | Mensaje: *"El documento de identidad o correo ya pertenece a un paciente registrado"* |
| **CP03** | Nombre vació: "", Apellido: "", Correo: "" | Intentar registro | Mensaje: *"Campos obligatorios requeridos"* |
| **CP04** | Correo con formato inválido: "anatorres.sin_arroba" | Intentar registro | Mensaje: *"Formato de correo electrónico inválido"* |
| **CP05** | Texto de búsqueda: "8934521" en campo de búsqueda | Buscar | La tabla muestra únicamente el expediente de Ana Torres |

**Adjunto:** Interfaz `paciente-list.component.html` (Directorio de Expedientes y modal *"Nuevo Paciente"*).

---

### HU 4 – Programación y Agendamiento de Citas Psicológicas (CU11)

#### Historia de Usuario:
**Como** Recepcionista o Paciente  
**quiero** programar una cita psicológica seleccionando terapeuta, fecha, hora y modalidad  
**para** asegurar la sesión de atención sin generar sobreposiciones en la agenda.

#### Descripción:
Permite reservar una consulta vinculando un paciente registrado con un psicólogo en un horario específico, seleccionando la duración (45, 50, 60 o 90 minutos), modalidad (Presencial o Teleconsulta virtual) y motivo de consulta.

#### Criterios de aceptación:
1. El sistema debe validar que el psicólogo tenga disponibilidad habilitada para el día y hora seleccionados.
2. No se permite reservar una cita en una fecha u hora anterior al momento actual (fechas pasadas).
3. Si el psicólogo ya cuenta con una cita en el mismo rango de horario, debe rechazar la reserva mostrando: *"El profesional ya tiene una cita agendada en ese horario"*.
4. Debe ser obligatorio seleccionar paciente, psicólogo, fecha y hora de inicio.
5. Al agendarse exitosamente, la cita se registra en estado *"Reservada"* y actualiza el contador de citas del día.

#### Casos de prueba funcionales (Caja negra):
| ID | Entrada | Acción | Salida esperada |
|---|---|---|---|
| **CP01** | Paciente: "Ana Torres", Psicólogo: "Dr. Carlos Mendoza", Fecha: Mañana, Hora: 10:00, Duración: 50 min, Modalidad: "Virtual" | Agendar turno | Cita registrada con éxito en estado "Reservada"; aparece en la agenda |
| **CP02** | Cita en fecha pasada (ej. Ayer a las 09:00) | Agendar turno | Error: *"No se pueden agendar citas en fechas u horas pasadas"* |
| **CP03** | Mismo psicólogo, misma fecha y hora (10:00) con otro paciente | Agendar turno | Error: *"El profesional ya tiene una cita agendada en ese horario"* |
| **CP04** | Formulario sin psicólogo seleccionado (Psicólogo="") | Agendar turno | Error: *"Debe seleccionar un psicólogo para agendar la sesión"* |
| **CP05** | Modalidad seleccionada: "Teleconsulta (virtual)" | Agendar turno | Cita agendada y habilitada automáticamente para generación de sala Jitsi Meet |

**Adjunto:** Interfaz `cita-agenda.component.html` (Agenda semanal y modal *"Agendar Nueva Consulta"*).

---

### HU 5 – Reprogramación y Cancelación de Citas Psicológicas (CU11)

#### Historia de Usuario:
**Como** Recepcionista o Terapeuta  
**quiero** reprogramar la fecha de una cita o cancelar una cita agendada  
**para** mantener la agenda actualizada ante imprevistos del paciente o del profesional y liberar horarios.

#### Descripción:
Permite modificar la fecha y hora de una cita en estado *"Reservada"* o *"Confirmada"*, validando que el nuevo horario esté libre. Asimismo, permite cancelar una cita registrando el cambio de estado para liberar el cupo.

#### Criterios de aceptación:
1. El sistema debe permitir cambiar la fecha y hora de una cita activa previa confirmación.
2. Si el nuevo horario propuesto coincide con otra cita del psicólogo, debe mostrar: *"El nuevo horario seleccionado no está disponible"*.
3. Al cancelar una cita, su estado debe cambiar inmediatamente a *"Cancelada"* y el cupo en la agenda debe quedar libre para nuevas reservas.
4. No se permite reprogramar ni cancelar citas que ya se encuentren en estado *"Finalizada"*.

#### Casos de prueba funcionales (Caja negra):
| ID | Entrada | Proceso | Salida esperada |
|---|---|---|---|
| **CP01** | Cita ID #101, Nueva fecha: Pasado mañana, Nueva hora: 15:00 (libre) | Reprogramar | Cita actualizada; estado cambia a "Reprogramada" con confirmación exitosa |
| **CP02** | Cita ID #101, Nueva hora: 11:00 (horario ocupado por otra cita) | Reprogramar | Mensaje de error: *"El nuevo horario seleccionado no está disponible"* |
| **CP03** | Cita ID #101, Clic en botón "Cancelar cita" y confirmar acción | Cancelar cita | Estado cambia a "Cancelada"; el cupo anterior queda disponible en agenda |
| **CP04** | Intento de reprogramar una cita con estado "Finalizada" | Reprogramar | Botón de acción deshabilitado o mensaje: *"No se puede modificar una cita concluida"* |

**Adjunto:** Interfaz `cita-agenda.component.html` (Modal *"Reprogramar Consulta"* y botón de cancelación).

---

### HU 6 – Dashboard de Indicadores y Alertas Clínicas (CU9 / CU10)

#### Historia de Usuario:
**Como** Administrador del Centro o Coordinador Clínico  
**quiero** visualizar en tiempo real los indicadores de citas del día y las alertas de priorización  
**para** supervisar la operatividad del centro y atender oportunamente pacientes con inasistencias o casos críticos.

#### Descripción:
Presenta un panel de control con métricas clave (citas de hoy, confirmadas, pendientes, inasistencias registradas, total de pacientes y terapeutas activos) y una sección de alertas de priorización clínica y operativa.

#### Criterios de aceptación:
1. El Dashboard debe calcular y desplegar las tarjetas KPI con datos actualizados en tiempo real: citas hoy, confirmadas, pendientes e inasistencias.
2. El panel debe permitir filtrar citas por estado (`all`, `reservada`, `confirmada`, `inasistencia`, `cancelada`) y por fecha.
3. Las alertas de priorización deben mostrar el nivel de severidad (Alta, Media, Baja) y el motivo de la alerta.
4. El usuario debe poder marcar una alerta como revisada/atendida, actualizando el contador.

#### Casos de prueba funcionales (Caja negra):
| ID | Entrada | Acción | Salida esperada |
|---|---|---|---|
| **CP01** | Acceso al Dashboard con 5 citas programadas hoy | Cargar vista | KPI "Citas Programadas Hoy" muestra el valor exacto de 5 |
| **CP02** | Registro de nueva cita para hoy desde otra pestaña | Refrescar panel | El contador de citas del día incrementa automáticamente en +1 |
| **CP03** | Selección de filtro de estado: "Inasistencia" | Aplicar filtro | La tabla del panel lista exclusivamente las citas no asistidas |
| **CP04** | Clic en "Marcar como atendida" sobre una alerta de inasistencia | Gestionar alerta | La alerta cambia de estado a "Atendida" y disminuye el contador de pendientes |

**Adjunto:** Interfaz `dashboard.component.html` y módulo `alerta-list.component.html`.

---

### HU 7 – Acceso y Conexión a Teleconsulta por Videoconferencia (CU13)

#### Historia de Usuario:
**Como** Psicólogo o Paciente con cita virtual  
**quiero** generar y acceder a la sala de videoconferencia encriptada mediante Jitsi Meet  
**para** llevar a cabo la sesión psicoterapéutica a distancia de manera confidencial y en tiempo real.

#### Descripción:
Permite la creación automática de una sala virtual segura vinculada a una cita en modalidad *"Virtual"*, generando enlaces seguros y diferenciados para el psicólogo y el paciente, con controles de estado (Iniciar, Entrar, Concluir, Cancelar).

#### Criterios de aceptación:
1. Solo se pueden generar salas virtuales para citas registradas bajo la modalidad *"Virtual"*.
2. El sistema debe generar un identificador de sala único (`room_name`) seguro y encriptado en el servidor Jitsi.
3. Al presionar *"Iniciar"*, el estado de la teleconsulta debe transicionar de `"programada"` a `"en_curso"`.
4. El psicólogo y el paciente deben poder copiar el enlace directo o abrir la sala incrustada en la plataforma.
5. Al hacer clic en *"Concluir"*, la sesión debe pasar a estado `"finalizada"` impidiendo nuevos accesos.

#### Casos de prueba funcionales (Caja negra):
| ID | Entrada | Proceso | Salida esperada |
|---|---|---|---|
| **CP01** | Cita virtual ID #105, Clic en "Generar sala virtual" | Crear sala | Sala generada con nombre único, estado "Programada" y enlace copiable |
| **CP02** | Teleconsulta en estado "Programada", Clic en "Iniciar" | Iniciar sesión | Estado cambia a "En curso", botón cambia a "Entrar" y registra hora de inicio |
| **CP03** | Clic en "Copiar link" del paciente | Copiar link | Enlace copiado al portapapeles con mensaje temporal "Copiado ✓" |
| **CP04** | Teleconsulta en estado "En curso", Clic en "Concluir" | Finalizar sesión | Estado cambia a "Finalizada"; se deshabilitan los botones de ingreso |
| **CP05** | Intento de generar sala para una cita presencial | Validar cita | Error: *"Solo las citas con modalidad virtual admiten sala de teleconsulta"* |

**Adjunto:** Interfaz `teleconsulta-list.component.html` (Salas virtuales de videoconferencia y controles Jitsi Meet).

---

## 3. PRUEBAS DE ACEPTACIÓN POR CASO DE USO (SPRINT 1)

> Formato oficial de ejecución paso a paso con precondiciones, resultados y estados de aceptación (Páginas 2, 3 y 4 de la guía docente).

---

### Prueba de caso de uso CU6: Gestionar Psicólogos y Perfiles Profesionales

| Campo | Detalle |
|---|---|
| **Caso de uso 6** | **Gestión de Psicólogos y Perfiles Profesionales** |
| **Descripción** | Permite registrar nuevos terapeutas, definir su modalidad de trabajo, asignar especialidades y habilitar o deshabilitar su estado en el centro. |
| **Precondiciones** | a) El usuario debe haber iniciado sesión con rol de Administrador de Centro.<br>b) El módulo "Equipo Terapéutico" debe estar habilitado.<br>c) Debe existir conexión activa con la base de datos PostgreSQL del tenant. |

#### Pasos de ejecución de la prueba:
| Paso | Acción | Resultado esperado | Estado |
|:---:|---|---|:---:|
| **1** | Acceder al módulo "Psicólogos" desde el menú lateral. | Se despliega el directorio con tarjetas de psicólogos, KPIs y barra de búsqueda. | **Satisfactorio** |
| **2** | Presionar el botón "+ Registrar Psicólogo". | Se abre el modal con los campos requeridos (nombre, apellido, correo, contraseña, modalidad y chips de especialidad). | **Satisfactorio** |
| **3** | Ingresar datos válidos de un nuevo terapeuta y presionar "Guardar". | El psicólogo es registrado exitosamente en el esquema del tenant y se añade al listado visual. | **Satisfactorio** |
| **4** | Intentar registrar otro psicólogo con el mismo correo ya existente. | El sistema rechaza la solicitud y muestra: *"Este correo electrónico ya se encuentra registrado"*. | **Satisfactorio** |
| **5** | Utilizar el interruptor toggle de estado para deshabilitar un psicólogo. | El estado cambia a inactivo y el contador de "Psicólogos Activos" disminuye en 1. | **Satisfactorio** |
| **6** | Escribir un criterio en la barra de búsqueda rápida. | La lista se filtra instantáneamente mostrando las coincidencias exactas. | **Satisfactorio** |

| Metadato | Valor |
|---|---|
| **Responsable** | Administrador del Centro / Equipo de Pruebas SCRUM |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | Interfaz web: `FRONTEND/src/app/modules/paquete2-gestion-clinica/components/psicologo-list/` (Directorio y Formulario Modal). |

---

### Prueba de caso de uso CU8: Gestionar Disponibilidad y Horarios de Psicólogos

| Campo | Detalle |
|---|---|
| **Caso de uso 8** | **Gestión de Disponibilidad y Horarios de Psicólogos** |
| **Descripción** | Permite configurar los turnos y franjas horarias de atención clínica semanal de cada profesional. |
| **Precondiciones** | a) El psicólogo debe existir y estar activo en el centro.<br>b) El operador debe tener permisos para modificar la disponibilidad del terapeuta. |

#### Pasos de ejecución de la prueba:
| Paso | Acción | Resultado esperado | Estado |
|:---:|---|---|:---:|
| **1** | En el directorio de psicólogos, presionar el botón "Gestionar Horarios" de un terapeuta. | Se despliega el modal *"Horarios y Disponibilidad Semanal"* con el historial de turnos del profesional. | **Satisfactorio** |
| **2** | Seleccionar día "Lunes", Hora inicio "08:00", Hora fin "12:00" y presionar "Añadir franja". | Se registra la franja horaria y se muestra en la tabla de turnos activos. | **Satisfactorio** |
| **3** | Ingresar intencionalmente una franja con Hora fin "07:30" (menor a la hora de inicio). | El sistema bloquea el guardado y muestra alerta de error de validación temporal. | **Satisfactorio** |
| **4** | Intentar agregar una franja "Lunes de 09:00 a 11:00" (solapamiento). | El sistema detecta el choque de horarios y emite el mensaje de conflicto de turno. | **Satisfactorio** |
| **5** | Presionar el botón de eliminar sobre una franja existente. | La franja es eliminada de la base de datos y la vista se actualiza inmediatamente. | **Satisfactorio** |

| Metadato | Valor |
|---|---|
| **Responsable** | Psicólogo / Coordinador Clínico |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | Interfaz modal: `showDisponibilidadModal` en `psicologo-list.component.html`. |

---

### Prueba de caso de uso CU7: Gestionar Pacientes y Expedientes

| Campo | Detalle |
|---|---|
| **Caso de uso 7** | **Gestión de Pacientes y Expedientes Clínicos** |
| **Descripción** | Administra el alta de pacientes, consulta de expedientes, datos demográficos, contactos de emergencia y búsqueda. |
| **Precondiciones** | a) Sesión iniciada con rol de Recepcionista o Administrador.<br>b) Módulo de Gestión Clínica activo y con permisos asignados. |

#### Pasos de ejecución de la prueba:
| Paso | Acción | Resultado esperado | Estado |
|:---:|---|---|:---:|
| **1** | Acceder a la sección "Gestión de Pacientes" desde el menú. | Se muestra la tabla de pacientes con columnas: Paciente/Correo, Documento, Género/Edad, Teléfono y Acciones. | **Satisfactorio** |
| **2** | Hacer clic en "+ Nuevo Paciente". | Se abre el formulario modal para ingresar datos de filiación del paciente. | **Satisfactorio** |
| **3** | Completar datos obligatorios (Nombre, Apellido, CI, Email) y presionar "Guardar". | Se crea el expediente clínico y el contador *"Total Pacientes Registrados"* se incrementa. | **Satisfactorio** |
| **4** | Intentar registrar un paciente con un documento de identidad ya existente. | Se muestra mensaje indicando que el número de documento ya está en uso. | **Satisfactorio** |
| **5** | Ingresar un nombre o número de documento en la caja de búsqueda. | La tabla filtra en tiempo real los registros que cumplen con el criterio. | **Satisfactorio** |

| Metadato | Valor |
|---|---|
| **Responsable** | Recepcionista / Administrador |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | Interfaz web: `FRONTEND/src/app/modules/paquete2-gestion-clinica/components/paciente-list/` (Tabla y Formulario). |

---

### Prueba de caso de uso CU11: Gestionar Citas y Agenda Psicológica

| Campo | Detalle |
|---|---|
| **Caso de uso 11** | **Gestión de Citas y Agenda Psicológica** |
| **Descripción** | Permite reservar nuevas consultas, consultar la agenda por fecha y estado, reprogramar turnos y cancelar citas. |
| **Precondiciones** | a) Paciente y psicólogo registrados en el tenant.<br>b) El psicólogo debe tener disponibilidad configurada en el día solicitado. |

#### Pasos de ejecución de la prueba:
| Paso | Acción | Resultado esperado | Estado |
|:---:|---|---|:---:|
| **1** | Ingresar al módulo "Agenda y Citas". | Se presenta la vista con KPIs diarios, filtros de fecha/estado y la grilla de citas. | **Satisfactorio** |
| **2** | Presionar "Agendar Nueva Cita". | Se despliega el formulario modal de reserva. | **Satisfactorio** |
| **3** | Seleccionar paciente, psicólogo, fecha futura, hora válida, duración y presionar "Reservar turno". | Cita registrada en estado `"Reservada"`; se añade a la tabla y se actualiza el contador de citas de hoy. | **Satisfactorio** |
| **4** | Intentar reservar un turno en un horario donde el profesional ya tiene cita. | El sistema deniega la reserva informando que el psicólogo se encuentra ocupado. | **Satisfactorio** |
| **5** | Seleccionar una cita y presionar "Reprogramar", eligiendo una nueva fecha y hora libres. | Se actualiza la fecha/hora de la cita y su estado pasa a `"Reprogramada"`. | **Satisfactorio** |
| **6** | Presionar el botón "Cancelar" en una cita y confirmar la acción. | La cita pasa a estado `"Cancelada"`; el horario queda liberado para nuevas reservas. | **Satisfactorio** |

| Metadato | Valor |
|---|---|
| **Responsable** | Recepcionista / Paciente |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | Interfaz web: `FRONTEND/src/app/modules/paquete3-agenda-comunicacion/components/cita-agenda/` (Tabla, Modal Reserva, Modal Reprogramación). |

---

### Prueba de caso de uso CU9 / CU10: Consultar Dashboard e Indicadores del Centro

| Campo | Detalle |
|---|---|
| **Caso de uso 9 / 10** | **Dashboard Administrativo, Indicadores y Alertas de Priorización** |
| **Descripción** | Despliega métricas consolidadas del centro (citas del día, inasistencias, terapeutas activos) y lista de alertas prioritarias. |
| **Precondiciones** | a) Usuario autenticado con rol directivo o administrativo.<br>b) Existencia de registros operativos en el centro. |

#### Pasos de ejecución de la prueba:
| Paso | Acción | Resultado esperado | Estado |
|:---:|---|---|:---:|
| **1** | Ingresar al módulo principal de Dashboard. | Se cargan los paneles KPI consolidados con datos del día en curso. | **Satisfactorio** |
| **2** | Verificar coherencia entre citas agendadas en base de datos y el valor del KPI. | La cifra mostrada en pantalla coincide con el total de registros en estado activo. | **Satisfactorio** |
| **3** | Seleccionar el filtro de fecha para revisar jornadas pasadas. | Las métricas y gráficos se recalculan en función del periodo seleccionado. | **Satisfactorio** |
| **4** | Acceder a la sección de alertas de priorización y verificar elementos pendientes. | Se listan las alertas ordenadas por nivel de severidad (Alta/Media/Baja). | **Satisfactorio** |
| **5** | Presionar "Marcar como atendida" sobre una alerta de inasistencia. | La alerta cambia de estado y el contador de notificaciones pendientes se actualiza. | **Satisfactorio** |

| Metadato | Valor |
|---|---|
| **Responsable** | Coordinador Clínico / Administrador |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | Interfaz web: `FRONTEND/src/app/modules/paquete1-admin-seguridad/components/dashboard/` y `alerta-list/`. |

---

### Prueba de caso de uso CU13: Gestionar Teleconsultas y Videoconferencias

| Campo | Detalle |
|---|---|
| **Caso de uso 13** | **Teleconsultas y Salas Virtuales (Jitsi Meet)** |
| **Descripción** | Genera y administra salas de videoconferencia seguras para sesiones remotas de psicoterapia. |
| **Precondiciones** | a) Cita psicológica previamente registrada con modalidad "Virtual".<br>b) Conexión a Internet y soporte de WebRTC en el navegador. |

#### Pasos de ejecución de la prueba:
| Paso | Acción | Resultado esperado | Estado |
|:---:|---|---|:---:|
| **1** | Acceder al módulo "Teleconsultas y Salas Virtuales". | Se visualiza la lista de salas con su estado (`Programada`, `En curso`, `Finalizada`). | **Satisfactorio** |
| **2** | Presionar "Generar sala virtual" para una cita virtual programada. | Se genera un `room_name` único y seguro, creándose el registro en estado `"Programada"`. | **Satisfactorio** |
| **3** | Presionar el botón "Copiar link" del enlace para el paciente. | El enlace de acceso es copiado al portapapeles y se visualiza la confirmación "Copiado ✓". | **Satisfactorio** |
| **4** | Presionar el botón "Iniciar" en una sala programada. | El estado cambia a `"En curso"`, registrando la marca de tiempo de inicio de la sesión. | **Satisfactorio** |
| **5** | Presionar "Entrar" o "Pestaña" para acceder a la sala Jitsi Meet. | Se abre la interfaz de videollamada con audio, video y chat seguros en tiempo real. | **Satisfactorio** |
| **6** | Al finalizar la consulta, presionar el botón "Concluir". | La sesión pasa a estado `"Finalizada"`, cerrando la sala e impidiendo nuevos accesos. | **Satisfactorio** |

| Metadato | Valor |
|---|---|
| **Responsable** | Psicólogo / Paciente / Equipo de Pruebas |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | Interfaz web: `FRONTEND/src/app/modules/paquete3-agenda-comunicacion/components/teleconsulta-list/` (Lista de Salas y controles Jitsi Meet). |

---

## 4. MATRIZ RESUMEN DE COBERTURA DE PRUEBAS (SPRINT 1)

| Caso de Uso | Historia de Usuario | Nro. Casos Caja Negra | Técnica Principal Aplicada | Estado de Aceptación |
|---|---|:---:|---|:---:|
| **CU6** | HU 1 – Directorio y Registro de Psicólogos | 5 (CP01 - CP05) | Partición de equivalencia y valores límite | **100% Satisfactorio** |
| **CU8** | HU 2 – Horarios y Disponibilidad Semanal | 5 (CP01 - CP05) | Valores límite y tablas de decisión | **100% Satisfactorio** |
| **CU7** | HU 3 – Registro y Directorio de Pacientes | 5 (CP01 - CP05) | Partición de equivalencia y unicidad | **100% Satisfactorio** |
| **CU11** | HU 4 – Programación y Reserva de Citas | 5 (CP01 - CP05) | Tablas de decisión y valores límite | **100% Satisfactorio** |
| **CU11** | HU 5 – Reprogramación y Cancelación | 4 (CP01 - CP04) | Transición de estados y disponibilidad | **100% Satisfactorio** |
| **CU9 / CU10** | HU 6 – Dashboard y Alertas Clínicas | 4 (CP01 - CP04) | Partición de equivalencia y cálculo dinámico | **100% Satisfactorio** |
| **CU13** | HU 7 – Teleconsultas y Videoconferencias | 5 (CP01 - CP05) | Transición de estados y seguridad | **100% Satisfactorio** |
| **TOTAL** | **7 Historias de Usuario de SP1** | **33 Casos de Prueba** | **Caja Negra Integral** | **APROBADO** |

---

## 5. CONCLUSIONES Y RECOMENDACIONES DE PRUEBAS (SP1)

1. **Efectividad de las Técnicas de Caja Negra:** La aplicación de partición de equivalencia en formularios y valores límite en la gestión de turnos permitió detectar y prevenir solapamientos de citas, inconsistencias horarias y duplicidad de registros en el esquema de base de datos.
2. **Aislamiento Multi-Tenant Garantizado:** Todas las pruebas de caja negra del Sprint 1 verificaron que las operaciones de consulta, creación y modificación de psicólogos, pacientes y citas se restringen rigurosamente al esquema (`tenant`) del centro autenticado.
3. **Validación del Flujo Clínico:** El ciclo de vida de las consultas psicológicas (desde su reserva, confirmación, eventual reprogramación o cancelación, hasta la ejecución de la teleconsulta virtual por Jitsi Meet) demostró transiciones de estado robustas y consistentes con la experiencia de usuario esperada.
