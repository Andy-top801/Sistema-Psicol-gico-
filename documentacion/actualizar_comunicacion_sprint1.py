# Script para actualizar los diagramas de comunicacion del Sprint 1 en intento.md
import os

new_text = '''A continuación se presentan los **Diagramas de Comunicación** bajo el estándar UML y el patrón de análisis **BCE (Boundary - Control - Entity / Interfaz - Control - Entidad)**, modelando la interacción horizontal de objetos con mensajería bidireccional numerada, generados directamente en **Enterprise Architect** e integrando código 100% compatible con **PlantText / PlantUML**:

#### Diagrama de Comunicación – CU6: Gestión de Psicólogos y Perfiles Profesionales (HU-11)

**Descripción del Flujo:** El Administrador del Centro accede al formulario de gestión de psicólogos e ingresa los datos personales, profesionales (número de colegiado) y tarifas base. El controlador valida la unicidad de credenciales en el tenant activo y crea transaccionalmente el usuario con rol psicólogo y su ficha profesional.

![Diagrama de Comunicación - CU6 Gestión de Psicólogos](imagenes/Diagrama%20de%20Comunicaci%C3%B3n%20-%20CU6%20Gestion%20de%20Psicologos.png)

**Código PlantText / PlantUML (Comunicación – CU6):**
```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial
skinparam backgroundColor #FAFBFD
left to right direction

skinparam actor {
    BackgroundColor #FFF2CC
    BorderColor #2C3E50
}
skinparam boundary {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam control {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam entity {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam arrow {
    Color #2C3E50
    FontColor #1A252C
    FontSize 11
}

actor "Administrador\\ndel Centro" as act
boundary "IU_GestionPsicologos\\n(Angular)" as iu
control "CTR_Psicologo\\n(Django)" as ctr
entity "CE_Usuario_y_Psicologo\\n(PostgreSQL)" as ce

act -- iu : 1: Ingresar datos de Psicólogo >\\n< 8: Mostrar confirmación
iu -- ctr : 2: POST /api/clinica/psicologos/ >\\n< 7: 201 Created
ctr -- ce : 3: Validar datos (email y colegiatura únicos) >\\n< 4: Datos válidos\\n5: Crear Usuario y Psicólogo en esquema tenant >\\n< 6: Registros creados exitosamente
@enduml
```

<br>

#### Diagrama de Comunicación – CU7: Gestión de Pacientes Web y Móvil (HU-13, HU-14)

**Descripción del Flujo:** El paciente (desde la app móvil o portal web) o el recepcionista registra los datos del paciente. Se valida la unicidad del documento de identidad en el tenant. Si el paciente es menor de edad, se exige la información del tutor responsable, generando automáticamente el número de expediente clínico.

![Diagrama de Comunicación - CU7 Gestión de Pacientes](imagenes/Diagrama%20de%20Comunicaci%C3%B3n%20-%20CU7%20Gestion%20de%20Pacientes.png)

**Código PlantText / PlantUML (Comunicación – CU7):**
```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial
skinparam backgroundColor #FAFBFD
left to right direction

skinparam actor {
    BackgroundColor #FFF2CC
    BorderColor #2C3E50
}
skinparam boundary {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam control {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam entity {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam arrow {
    Color #2C3E50
    FontColor #1A252C
    FontSize 11
}

actor "Recepcionista /\\nPaciente" as act
boundary "IU_RegistroPacientes\\n(Angular / Móvil)" as iu
control "CTR_Paciente\\n(Django REST)" as ctr
entity "CE_Paciente_y_Expediente\\n(PostgreSQL)" as ce

act -- iu : 1: Ingresar datos (CI, fecha nac, tutor si menor) >\\n< 8: Mostrar 'Expediente clínico generado'
iu -- ctr : 2: POST /api/clinica/pacientes/ + Header Tenant >\\n< 7: 201 Created {paciente_id, expediente}
ctr -- ce : 3: Validar unicidad de CI en tenant activo >\\n< 4: Documento no duplicado y tutor válido\\n5: INSERT INTO clinica_paciente con código único >\\n< 6: Paciente registrado en esquema tenant
@enduml
```

<br>

#### Diagrama de Comunicación – CU8: Gestión de Disponibilidad y Horarios de Psicólogos (HU-12)

**Descripción del Flujo:** El terapeuta o administrador establece las franjas horarias semanales y la duración por bloque. El controlador comprueba que las horas de inicio sean coherentes y que no existan traslapes entre intervalos del mismo profesional, persistiendo la disponibilidad y dividiendo las franjas en bloques consultables.

![Diagrama de Comunicación - CU8 Gestión de Disponibilidad](imagenes/Diagrama%20de%20Comunicaci%C3%B3n%20-%20CU8%20Gestion%20de%20Disponibilidad.png)

**Código PlantText / PlantUML (Comunicación – CU8):**
```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial
skinparam backgroundColor #FAFBFD
left to right direction

skinparam actor {
    BackgroundColor #FFF2CC
    BorderColor #2C3E50
}
skinparam boundary {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam control {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam entity {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam arrow {
    Color #2C3E50
    FontColor #1A252C
    FontSize 11
}

actor "Psicólogo /\\nAdministrador" as act
boundary "IU_DisponibilidadHoraria\\n(Angular)" as iu
control "CTR_Disponibilidad\\n(Django REST)" as ctr
entity "CE_Disponibilidad_y_Horario\\n(PostgreSQL)" as ce

act -- iu : 1: Configurar franjas semanales y duración bloque >\\n< 8: Mostrar 'Horario laboral actualizado'
iu -- ctr : 2: POST /api/clinica/disponibilidad/ + JWT >\\n< 7: 200 OK {franjas_configuradas, slots_generados}
ctr -- ce : 3: Validar coherencia (inicio < fin) sin traslapes >\\n< 4: Franjas válidas y terapeuta activo\\n5: Guardar franjas y particionar bloques en DB >\\n< 6: Disponibilidad persistida en esquema
@enduml
```

<br>

#### Diagrama de Comunicación – CU9: Consultar Dashboard e Indicadores Clínicos (HU-20)

**Descripción del Flujo:** El Coordinador Clínico o Administrador solicita la visualización del panel de mando. El controlador ejecuta consultas agregadas optimizadas en PostgreSQL (conteo de citas, ausentismo y ocupación agrupados por terapeuta) y retorna los KPIs para renderizarlos interactivamente en Angular.

![Diagrama de Comunicación - CU9 Dashboard Clínico](imagenes/Diagrama%20de%20Comunicaci%C3%B3n%20-%20CU9%20Dashboard%20Clinico.png)

**Código PlantText / PlantUML (Comunicación – CU9):**
```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial
skinparam backgroundColor #FAFBFD
left to right direction

skinparam actor {
    BackgroundColor #FFF2CC
    BorderColor #2C3E50
}
skinparam boundary {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam control {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam entity {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam arrow {
    Color #2C3E50
    FontColor #1A252C
    FontSize 11
}

actor "Coordinador /\\nAdministrador" as act
boundary "IU_DashboardClinico\\n(Angular 17)" as iu
control "CTR_Dashboard\\n(Django REST)" as ctr
entity "CE_Metricas_y_Citas\\n(PostgreSQL)" as ce

act -- iu : 1: Acceder al Dashboard y seleccionar período >\\n< 8: Renderizar KPIs, gráficos de tasa y métricas
iu -- ctr : 2: GET /api/agenda/dashboard/kpis/?periodo=mes >\\n< 7: 200 OK {total_citas, ausentismo, ocupacion}
ctr -- ce : 3: Validar permisos y esquema tenant >\\n< 4: Contexto administrativo autorizado\\n5: SELECT COUNT, AVG(tasa_ausentismo) GROUP BY terapeuta >\\n< 6: Agregaciones estadísticas calculadas
@enduml
```

<br>

#### Diagrama de Comunicación – CU10: Gestión de Alertas Tempranas y Priorización (HU-21)

**Descripción del Flujo:** El sistema analiza el historial de asistencias de los pacientes en el esquema del centro. Si se identifican 2 o más inasistencias consecutivas, el servicio genera una alerta con nivel ALTO, listando de inmediato a los pacientes en riesgo de deserción en la bandeja del equipo terapéutico.

![Diagrama de Comunicación - CU10 Alertas Tempranas](imagenes/Diagrama%20de%20Comunicaci%C3%B3n%20-%20CU10%20Alertas%20Tempranas.png)

**Código PlantText / PlantUML (Comunicación – CU10):**
```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial
skinparam backgroundColor #FAFBFD
left to right direction

skinparam actor {
    BackgroundColor #FFF2CC
    BorderColor #2C3E50
}
skinparam boundary {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam control {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam entity {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam arrow {
    Color #2C3E50
    FontColor #1A252C
    FontSize 11
}

actor "Coordinador /\\nPsicólogo" as act
boundary "IU_AlertasClinicas\\n(Angular)" as iu
control "CTR_AlertaService\\n(Django REST)" as ctr
entity "CE_Alerta_y_Asistencia\\n(PostgreSQL)" as ce

act -- iu : 1: Consultar bandeja de alertas prioritarias >\\n< 8: Desplegar lista de pacientes en riesgo de abandono
iu -- ctr : 2: GET /api/agenda/alertas/?resuelta=false >\\n< 7: 200 OK {alertas_activas, nivel_riesgo: ALTO}
ctr -- ce : 3: Evaluar historial de inasistencias consecutivas (2+) >\\n< 4: Pacientes con ausentismo crítico identificados\\n5: INSERT / UPDATE agenda_alerta (prioridad='ALTA') >\\n< 6: Alertas clínicas registradas en esquema
@enduml
```

<br>

#### Diagrama de Comunicación – CU11: Programación, Reserva y Gestión de Citas (HU-15, HU-16, HU-17, HU-22)

**Descripción del Flujo:** Al reservar una sesión, el recepcionista o paciente selecciona el psicólogo, fecha, bloque y modalidad. El backend abre una transacción con bloqueo pesimista `SELECT FOR UPDATE` para evitar colisiones en citas simultáneas. Tras validar la ausencia de solapamiento, confirma la cita con estado `PROGRAMADA` y expide el comprobante.

![Diagrama de Comunicación - CU11 Gestión de Citas y Agenda](imagenes/Diagrama%20de%20Comunicaci%C3%B3n%20-%20CU11%20Gestion%20de%20Citas%20y%20Agenda.png)

**Código PlantText / PlantUML (Comunicación – CU11):**
```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial
skinparam backgroundColor #FAFBFD
left to right direction

skinparam actor {
    BackgroundColor #FFF2CC
    BorderColor #2C3E50
}
skinparam boundary {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam control {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam entity {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam arrow {
    Color #2C3E50
    FontColor #1A252C
    FontSize 11
}

actor "Recepcionista /\\nPaciente" as act
boundary "IU_AgendaCitas\\n(Angular / Móvil)" as iu
control "CTR_CitaService\\n(Django REST)" as ctr
entity "CE_Cita_y_Disponibilidad\\n(PostgreSQL)" as ce

act -- iu : 1: Seleccionar paciente, terapeuta, fecha y slot >\\n< 8: Desplegar comprobante de cita confirmada
iu -- ctr : 2: POST /api/agenda/citas/ {fecha, hora, modalidad} >\\n< 7: 201 Created {cita_id, estado: 'PROGRAMADA'}
ctr -- ce : 3: Iniciar tx y SELECT FOR UPDATE sobre slot >\\n< 4: Bloqueo pesimista concedido (slot libre)\\n5: INSERT INTO agenda_cita y marcar slot ocupado >\\n< 6: Cita registrada sin colisión horaria
@enduml
```

<br>

#### Diagrama de Comunicación – CU13: Gestión de Teleconsultas y Videoconferencias Jitsi Meet (HU-18, HU-19)

**Descripción del Flujo:** El terapeuta o paciente accede a la cita virtual en el horario correspondiente (+/- 15 min). El controlador comprueba la vigencia de la cita y genera los tokens JWT de moderador (terapeuta) o participante (paciente), embebiendo la sala interactiva de Jitsi Meet con controles de llamada y cifrado.

![Diagrama de Comunicación - CU13 Teleconsulta Jitsi Meet](imagenes/Diagrama%20de%20Comunicaci%C3%B3n%20-%20CU13%20Teleconsulta%20Jitsi%20Meet.png)

**Código PlantText / PlantUML (Comunicación – CU13):**
```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial
skinparam backgroundColor #FAFBFD
left to right direction

skinparam actor {
    BackgroundColor #FFF2CC
    BorderColor #2C3E50
}
skinparam boundary {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam control {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam entity {
    BackgroundColor #FFF2DE
    BorderColor #2C3E50
}
skinparam arrow {
    Color #2C3E50
    FontColor #1A252C
    FontSize 11
}

actor "Terapeuta /\\nPaciente" as act
boundary "IU_Teleconsulta\\n(Angular / Móvil)" as iu
control "CTR_Teleconsulta\\n(Django REST)" as ctr
entity "CE_Sala_y_Cita\\n(PostgreSQL)" as ce

act -- iu : 1: Clic en 'Unirse a Teleconsulta' >\\n< 8: Embeber sala Jitsi Meet con controles de llamada
iu -- ctr : 2: GET /api/agenda/teleconsulta/{id}/access/ + JWT >\\n< 7: 200 OK {room_name, jwt_token, rol_moderador}
ctr -- ce : 3: Validar ventana horaria activa (cita +/- 15 min) >\\n< 4: Cita virtual vigente y usuario participante\\n5: INSERT INTO agenda_teleconsulta (room, fecha_inicio) >\\n< 6: Sala registrada y credenciales generadas
@enduml
```

---

'''

fpath = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\documentacion\intento.md'
with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
    orig = f.read()

# Buscamos exactamente el inicio y el final de la subseccion
start_tag = "A continuación se presentan los **Diagramas de Comunicación**"
if start_tag not in orig:
    # Buscar por coincidencia parcial
    for line in orig.splitlines():
        if "Diagramas de Comunicación" in line and "4.2.1.3" not in line:
            start_tag = line
            break

end_tag = "### 4.2.2 Implementación"
if end_tag not in orig:
    for line in orig.splitlines():
        if "4.2.2 Implementación" in line or "4.2.2 Implementaci" in line:
            end_tag = line
            break

pos_start = orig.find(start_tag)
pos_end = orig.find(end_tag)

print(f"pos_start: {pos_start}, pos_end: {pos_end}")

if pos_start != -1 and pos_end != -1:
    updated = orig[:pos_start] + new_text + orig[pos_end:]
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(updated)
    print(f"intento.md actualizado exitosamente con 7 diagramas de comunicación. Tamaño final: {len(updated)}")
else:
    print("Error: No se encontraron los marcadores en intento.md")
