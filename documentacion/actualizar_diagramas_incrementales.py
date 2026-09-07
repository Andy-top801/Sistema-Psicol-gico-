# -*- coding: utf-8 -*-
import re

CU_DIAGRAM_MD = """#### Diagrama de Casos de Uso del Sprint 1 (Modelo Incremental Sprint 0 + Sprint 1)
En estricto apego a la naturaleza iterativa e incremental del marco de trabajo ágil SCRUM, el diagrama de casos de uso del Sprint 1 consolida la totalidad de las capacidades funcionales acumuladas en la plataforma: preserva e integra los casos de uso base construidos en el Sprint 0 (`CU1: Gestionar centros psicológicos y Multi-Tenant`, `CU2: Autenticar e iniciar sesión JWT`, `CU3: Gestionar usuarios institucionales`, `CU4: Gestionar roles y permisos RBAC` y `CU27: Recuperar credenciales y contraseña`) junto a los nuevos casos de uso propios del incremento del Sprint 1 (`CU6: Gestionar psicólogos`, `CU7: Gestionar expediente de pacientes`, `CU8: Configurar disponibilidad horaria`, `CU9: Consultar Dashboard e indicadores`, `CU10: Gestionar alertas de priorización`, `CU11: Gestionar citas y agenda psicológica` y `CU13: Realizar teleconsulta y videoconferencias Jitsi Meet`), articulando de forma unificada a los 6 actores del sistema.

**Código PlantText / PlantUML (Casos de Uso - Sprint 1 Incremental):**
```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

actor "SuperAdministrador\\n(Plataforma)" as superadmin
actor "Administrador del Centro" as admin
actor "Coordinador Clínico" as coord
actor "Psicólogo" as psyc
actor "Recepcionista" as recep
actor "Paciente\\n(Web / Móvil)" as patient

rectangle "Plataforma SIGEPSI - Sistema Acumulado (Sprint 0 + Sprint 1)" {

  rectangle "Incremento Sprint 0: Base Multi-Tenant, Seguridad & Acceso" #F2F4F4 {
    usecase "CU1: Gestionar centros psicológicos\\ny configuración Multi-Tenant" as CU1
    usecase "CU2: Autenticar e iniciar sesión (JWT)" as CU2
    usecase "CU3: Gestionar usuarios institucionales" as CU3
    usecase "CU4: Gestionar roles y permisos (RBAC)" as CU4
    usecase "CU27: Recuperar credenciales y contraseña" as CU27
  }

  rectangle "Incremento Sprint 1: Atención Clínica, Agenda & Teleconsulta" #FEF9E7 {
    usecase "CU6: Gestionar psicólogos y\\nperfiles profesionales" as CU6
    usecase "CU8: Configurar disponibilidad horaria\\ny carga de trabajo" as CU8
    usecase "CU7: Gestionar expediente y\\ndatos de pacientes" as CU7
    usecase "CU11: Gestionar citas y\\nagenda psicológica" as CU11
    usecase "CU13: Realizar teleconsulta y\\nvideoconferencia (Jitsi Meet)" as CU13
    usecase "CU9: Consultar Dashboard e\\nindicadores del centro" as CU9
    usecase "CU10: Gestionar alertas de\\npriorización y seguimiento" as CU10

    usecase "Validar colisión de horarios" as val_overlap
  }
}

' Asociaciones SuperAdmin
superadmin --> CU1

' Asociaciones Administrador del Centro
admin --> CU2
admin --> CU3
admin --> CU4
admin --> CU6
admin --> CU7
admin --> CU9

' Asociaciones Coordinador Clínico
coord --> CU2
coord --> CU6
coord --> CU9
coord --> CU10
coord --> CU11

' Asociaciones Psicólogo
psyc --> CU2
psyc --> CU8
psyc --> CU11
psyc --> CU13
psyc --> CU10

' Asociaciones Recepcionista
recep --> CU2
recep --> CU7
recep --> CU11

' Asociaciones Paciente (Web / Móvil)
patient --> CU2
patient --> CU27
patient --> CU7
patient --> CU11
patient --> CU13

' Inclusiones obligatorias
CU11 ..> val_overlap : <<include>>
CU6 ..> CU2 : <<include>>
CU7 ..> CU2 : <<include>>
CU11 ..> CU2 : <<include>>
CU13 ..> CU2 : <<include>>
CU9 ..> CU2 : <<include>>
CU3 ..> CU2 : <<include>>
CU4 ..> CU2 : <<include>>
@enduml
```"""

CLASS_DIAGRAM_MD = """#### Diagrama de Clases del Sprint 1 (Modelo Incremental Sprint 0 + Sprint 1)
Representa la arquitectura estructural de dominio completa y acumulada del sistema, integrando de manera rigurosa las entidades base del **Sprint 0** (esquema global `public` con `Tenant`, `Dominio` y `SuperAdmin`, junto con las entidades institucionales y de control de acceso del esquema `tenant`: `Centro`, `Usuario`, `Rol`, `Permiso`, `TokenAcceso` y `TokenRecuperacion`) con las nuevas entidades del incremento del **Sprint 1** (`Psicologo`, `Especialidad`, `DisponibilidadHoraria`, `Paciente`, `Cita`, `Teleconsulta` y `AlertaPriorizacion`), especificando atributos tipados, operaciones, cardinalidades y tipos de asociación (composición, agregación, especialización conceptual y dependencias).

**Código PlantText / PlantUML (Diagrama de Clases - Sprint 1 Incremental):**
```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

package "Esquema Public (Global - Consolidado Sprint 0)" #F2F4F4 {
  class Tenant {
    + id: UUID
    + nombre: String
    + slug: String
    + schema_name: String
    + plan: String
    + activo: Boolean
    + fecha_creacion: DateTime
    + crear_esquema()
    + suspender()
  }

  class Dominio {
    + id: Integer
    + dominio: String
    + es_primario: Boolean
  }

  class SuperAdmin {
    + id: Integer
    + email: String
    + password_hash: String
    + nombre: String
    + activo: Boolean
    + gestionar_tenants()
  }
}

package "Esquema Tenant: Centro Psicológico (Aislado)" {
  package "Módulo Base, Usuarios y Seguridad (Consolidado Sprint 0)" #E8F8F5 {
    class Centro {
      + id: UUID
      + nombre: String
      + direccion: String
      + telefono: String
      + email: String
      + logo: String
      + horarios_atencion: JSON
      + actualizar_config()
    }

    class Usuario {
      + id: UUID
      + email: String
      + password_hash: String
      + nombre: String
      + apellido: String
      + telefono: String
      + activo: Boolean
      + fecha_creacion: DateTime
      + autenticar(password)
      + cerrar_sesion()
    }

    class Rol {
      + id: Integer
      + nombre: String
      + descripcion: String
    }

    class Permiso {
      + id: Integer
      + nombre: String
      + codigo: String
      + modulo: String
    }

    class TokenAcceso {
      + id: UUID
      + token_jwt: String
      + fecha_expiracion: DateTime
      + es_valido(): Boolean
    }

    class TokenRecuperacion {
      + id: UUID
      + token: String
      + fecha_expiracion: DateTime
      + usado: Boolean
      + validar_token(): Boolean
    }
  }

  package "Módulo Clínico, Agenda y Teleconsulta (Incremento Sprint 1)" #FEF9E7 {
    class Psicologo {
      + id: UUID
      + numero_colegiado: String
      + biografia: Text
      + modalidad: String
      + tarifa_base: Decimal
      + activo: Boolean
      + obtener_carga_semanal(): Integer
    }

    class Especialidad {
      + id: Integer
      + nombre: String
      + descripcion: String
    }

    class DisponibilidadHoraria {
      + id: UUID
      + dia_semana: Integer
      + hora_inicio: Time
      + hora_fin: Time
      + duracion_bloque_min: Integer
      + activo: Boolean
      + es_bloque_valido(): Boolean
    }

    class Paciente {
      + id: UUID
      + codigo_expediente: String
      + ci: String
      + fecha_nacimiento: Date
      + genero: String
      + contacto_emergencia_nombre: String
      + contacto_emergencia_telf: String
      + es_menor_edad(): Boolean
    }

    class Cita {
      + id: UUID
      + fecha: Date
      + hora_inicio: Time
      + hora_fin: Time
      + modalidad: String
      + estado: String
      + motivo_consulta: Text
      + costo: Decimal
      + reprogramar(nueva_fecha, nueva_hora)
      + cancelar(motivo)
    }

    class Teleconsulta {
      + id: UUID
      + sala_id: String
      + jwt_room_token: String
      + duracion_segundos: Integer
      + estado_conexion: String
      + iniciar_sala(): String
      + finalizar_sala()
    }

    class AlertaPriorizacion {
      + id: UUID
      + tipo: String
      + severidad: String
      + descripcion: Text
      + resuelta: Boolean
      + fecha_creacion: DateTime
      + resolver(observacion)
    }
  }
}

' Relaciones Globales (Sprint 0)
Tenant "1" *-- "1..*" Dominio : posee
Tenant "1" -- "1" Centro : aprovisiona
SuperAdmin ..> Tenant : administra

' Relaciones Base Tenant (Sprint 0)
Centro "1" *-- "0..*" Usuario : agrupa
Centro "1" *-- "0..*" Cita : registra
Usuario "0..*" --> "1" Rol : asignado
Rol "0..*" o-- "1..*" Permiso : concede
Usuario "1" *-- "0..*" TokenAcceso : genera
Usuario "1" *-- "0..*" TokenRecuperacion : solicita

' Relaciones Incrementales (Sprint 1)
Usuario "1" -- "0..1" Psicologo : perfil profesional
Usuario "1" -- "0..1" Paciente : perfil clínico
Psicologo "1" *-- "1..*" DisponibilidadHoraria : programa
Psicologo "0..*" -- "1..*" Especialidad : acredita
Psicologo "1" -- "0..*" Cita : atiende
Paciente "1" -- "0..*" Cita : agenda
Cita "1" *-- "0..1" Teleconsulta : genera
Paciente "1" -- "0..*" AlertaPriorizacion : origina
@enduml
```"""

ARCH_DIAGRAM_MD = """**Código PlantText / PlantUML (Diagrama de Arquitectura de 3 Capas - Sprint 1):**
```plantuml
@startuml
skinparam packageStyle rectangle
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
skinparam linetype ortho

package "Capa 1: Presentación (Clientes Web y Móvil - Sistema Acumulado)" #EBF5FB {
  node "Cliente Web (Navegador Chrome/Edge/Firefox)" {
    component "SPA Angular 17" as AngularApp {
      [Auth & Multi-Tenant Guard (SP0)]
      [Gestión Usuarios & Roles (SP0)]
      [Configuración Centro (SP0)]
      [Módulo Psicólogos & Disponibilidad (SP1)]
      [Módulo Expediente Pacientes (SP1)]
      [Calendario Interactivo Citas (SP1)]
      [Dashboard Métricas & Alertas (SP1)]
      [Jitsi Meet WebRTC Wrapper (SP1)]
      [HTTP Interceptor (JWT + Tenant)]
    }
  }

  node "Cliente Móvil (Android / iOS)" {
    component "App Nativa Flutter 3.x" as FlutterApp {
      [Login & Tenant Selector (SP0)]
      [Perfil & Datos Paciente (SP1)]
      [Pantalla Mis Citas & Reservar (SP1)]
      [Jitsi Meet Native SDK Screen (SP1)]
      [Secure Storage (Tokens)]
    }
  }
}

package "Capa 2: Lógica de Negocio (Servicios Backend Django / DRF)" #FEF9E7 {
  node "Servidor Django 5.x / DRF" {
    component "API Gateway & Endpoints REST Acumulados" as Endpoints {
      [/api/auth/ & /api/accounts/ (SP0)]
      [/api/tenants/ & /api/core/ (SP0)]
      [/api/clinica/psicologos/ (SP1)]
      [/api/clinica/pacientes/ (SP1)]
      [/api/agenda/citas/ (SP1)]
      [/api/agenda/teleconsulta/ (SP1)]
      [/api/agenda/dashboard/ (SP1)]
    }

    component "Servicios de Dominio" as Services {
      [TenantIsolationService (SP0)]
      [AuthJWTService (SP0)]
      [AvailabilityValidator (SP1)]
      [ConflictResolutionService (SP1)]
      [JitsiTokenGenerator (SP1)]
      [MetricsAggregator (SP1)]
    }

    component "Capa de Middleware" as Middleware {
      [TenantMiddleware (django-tenants)]
      [JWTAuthentication]
      [RolePermissionGuard]
    }

    component "Django ORM" as ORM
  }

  node "Infraestructura de Videoconferencia" {
    component "Servidor Jitsi Meet (WebRTC SFU)" as JitsiServer {
      [VideoBridge (JVB)]
      [Prosody XMPP Server]
    }
  }
}

package "Capa 3: Datos (PostgreSQL 16 Multi-Tenant Acumulado)" #EAFAF1 {
  database "Motor PostgreSQL 16" {
    frame "Esquema Public (Global - Consolidado Sprint 0)" {
      [tenants_tenant]
      [tenants_dominio]
      [accounts_superadmin]
    }

    frame "Esquema Tenant: Centro Psicológico (Aislado)" {
      folder "Tablas Base (Consolidado Sprint 0)" {
        [core_centro]
        [accounts_usuario]
        [accounts_rol]
        [accounts_permiso]
        [accounts_rol_permiso]
        [accounts_token_recuperacion]
      }
      folder "Tablas Clínicas & Agenda (Incremento Sprint 1)" {
        [clinica_especialidad]
        [clinica_psicologo]
        [clinica_psicologo_especialidad]
        [clinica_disponibilidad]
        [clinica_paciente]
        [agenda_cita]
        [agenda_teleconsulta]
        [agenda_alerta]
      }
    }
  }
}

AngularApp --> Endpoints : "HTTPS / JSON REST API"
FlutterApp --> Endpoints : "HTTPS / JSON REST API"
AngularApp ..> JitsiServer : "WebRTC Audio/Video Stream"
FlutterApp ..> JitsiServer : "WebRTC Native Media Stream"

Endpoints --> Middleware
Middleware --> Services
Services --> ORM
ORM --> "Esquema Public (Global - Consolidado Sprint 0)" : "search_path = public"
ORM --> "Esquema Tenant: Centro Psicológico (Aislado)" : "search_path = tenant_schema"
@enduml
```"""

DATA_DESIGN_MD = """#### 4.2.1.2 Diseño de Datos (Modelo Relacional Acumulado: Sprint 0 + Sprint 1)
En estricta conformidad con el principio metodológico de desarrollo ágil iterativo e incremental, el modelo de datos de la plataforma SIGEPSI en el Sprint 1 no reemplaza al modelo previo, sino que **adiciona e integra orgánicamente sus nuevas entidades clínicas, de agenda y teleconsulta sobre la arquitectura Multi-Tenant por esquemas consolidada en el Sprint 0**.

El sistema completo acumula **17 tablas relacionales** organizadas bajo la estructura Multi-Tenant de PostgreSQL:

##### 1. Esquema `public` (Global / Multi-Tenant – Consolidado Sprint 0)
Tablas compartidas a nivel de plataforma para el aprovisionamiento, enrutamiento y administración de los centros:

| Tabla | Campos Principales | Tipo de Datos | Descripción de Regla de Negocio |
| :--- | :--- | :--- | :--- |
| `tenants_tenant` | `id`<br>`nombre`<br>`slug`<br>`schema_name`<br>`plan`<br>`activo`<br>`fecha_creacion` | UUID (PK)<br>Varchar(100)<br>Varchar(100) UNIQUE<br>Varchar(63) UNIQUE<br>Varchar(20)<br>Boolean<br>DateTime | Registro maestro de cada centro psicológico suscrito; define el nombre del esquema PostgreSQL aislado. |
| `tenants_dominio` | `id`<br>`tenant_id`<br>`dominio`<br>`es_primario` | Serial (PK)<br>UUID (FK Tenant)<br>Varchar(253) UNIQUE<br>Boolean | Enrutamiento de subdominios o dominios personalizados vinculados al centro. |
| `accounts_superadmin` | `id`<br>`email`<br>`password_hash`<br>`nombre`<br>`apellido`<br>`activo`<br>`fecha_creacion` | Serial (PK)<br>Varchar(254) UNIQUE<br>Varchar(255)<br>Varchar(150)<br>Varchar(150)<br>Boolean<br>DateTime | Cuenta con privilegios globales para crear, suspender o monitorear tenants en la plataforma. |

<br>

##### 2. Esquema por `tenant` (Base Institucional y Usuarios – Consolidado Sprint 0)
Tablas aisladas e independientes replicadas dentro del esquema de cada centro psicológico:

| Tabla | Campos Principales | Tipo de Datos | Descripción de Regla de Negocio |
| :--- | :--- | :--- | :--- |
| `core_centro` | `id`<br>`nombre`<br>`direccion`<br>`telefono`<br>`email`<br>`logo`<br>`horarios_atencion`<br>`configuracion` | UUID (PK)<br>Varchar(200)<br>Varchar(255)<br>Varchar(30)<br>Varchar(254)<br>Varchar(255)<br>JSONB<br>JSONB | Identidad institucional, logotipo y parámetros operativos propios de la clínica o consultorio. |
| `accounts_usuario` | `id`<br>`email`<br>`password_hash`<br>`nombre`<br>`apellido`<br>`telefono`<br>`rol_id`<br>`activo`<br>`fecha_creacion` | UUID (PK)<br>Varchar(254) UNIQUE<br>Varchar(255)<br>Varchar(150)<br>Varchar(150)<br>Varchar(30)<br>Integer (FK Rol)<br>Boolean<br>DateTime | Cuenta de usuario perteneciente al centro (Admin, Psicólogo, Recepcionista, Coordinador o Paciente). |
| `accounts_rol` | `id`<br>`nombre`<br>`descripcion` | Serial (PK)<br>Varchar(50) UNIQUE<br>Text | Catálogo de roles de seguridad institucionales bajo el modelo RBAC. |
| `accounts_permiso` | `id`<br>`nombre`<br>`codigo`<br>`modulo`<br>`descripcion` | Serial (PK)<br>Varchar(100)<br>Varchar(100) UNIQUE<br>Varchar(50)<br>Text | Permisos atómicos del sistema (ej. `clinica.view_psicologo`, `agenda.book_cita`). |
| `accounts_rol_permiso` | `id`<br>`rol_id`<br>`permiso_id` | Serial (PK)<br>Integer (FK Rol)<br>Integer (FK Permiso) | Matriz de permisos asignados a cada rol del centro psicológico. |
| `accounts_token_recuperacion` | `id`<br>`usuario_id`<br>`token`<br>`fecha_expiracion`<br>`usado` | UUID (PK)<br>UUID (FK Usuario)<br>Varchar(100) UNIQUE<br>DateTime<br>Boolean | Tokens unívocos de un solo uso para el restablecimiento seguro de credenciales olvidadas. |

<br>

##### 3. Esquema por `tenant` (Módulo Clínico, Agenda y Teleconsulta – Incremento Sprint 1)
Nuevas tablas operativas incorporadas en el incremento del Sprint 1, vinculadas a las cuentas de usuario:

| Tabla | Campos Principales | Tipo de Datos | Descripción de Regla de Negocio |
| :--- | :--- | :--- | :--- |
| `clinica_especialidad` | `id`<br>`nombre`<br>`descripcion` | Serial (PK)<br>Varchar(100)<br>Text | Catálogo de especialidades clínicas (Infantil, Parejas, Cognitivo-Conductual, Neuropsicología). |
| `clinica_psicologo` | `id`<br>`usuario_id`<br>`numero_colegiado`<br>`biografia`<br>`modalidad`<br>`tarifa_base`<br>`activo` | UUID (PK)<br>UUID (FK Usuario) UNIQUE<br>Varchar(50) UNIQUE<br>Text<br>Varchar(20)<br>Decimal(10,2)<br>Boolean | Perfil profesional de salud mental vinculado biunívocamente al usuario institucional. |
| `clinica_psicologo_especialidad` | `id`<br>`psicologo_id`<br>`especialidad_id` | Serial (PK)<br>UUID (FK Psicologo)<br>Integer (FK Especialidad) | Relación muchos a muchos entre terapeutas y especialidades dominadas. |
| `clinica_disponibilidad` | `id`<br>`psicologo_id`<br>`dia_semana`<br>`hora_inicio`<br>`hora_fin`<br>`duracion_bloque_min`<br>`activo` | UUID (PK)<br>UUID (FK Psicologo)<br>SmallInt (0=Dom...6=Sáb)<br>Time<br>Time<br>SmallInt<br>Boolean | Matriz de horarios laborales para autogeneración de intervalos de cita libres. |
| `clinica_paciente` | `id`<br>`usuario_id`<br>`codigo_expediente`<br>`ci`<br>`fecha_nacimiento`<br>`genero`<br>`contacto_emergencia_nombre`<br>`contacto_emergencia_telf` | UUID (PK)<br>UUID (FK Usuario) UNIQUE<br>Varchar(30) UNIQUE<br>Varchar(20) UNIQUE<br>Date<br>Varchar(1)<br>Varchar(120)<br>Varchar(25) | Ficha general y expediente sociodemográfico del paciente atendido en el centro. |
| `agenda_cita` | `id`<br>`paciente_id`<br>`psicologo_id`<br>`fecha`<br>`hora_inicio`<br>`hora_fin`<br>`modalidad`<br>`estado`<br>`motivo_consulta`<br>`costo` | UUID (PK)<br>UUID (FK Paciente)<br>UUID (FK Psicologo)<br>Date<br>Time<br>Time<br>Varchar(20)<br>Varchar(25)<br>Text<br>Decimal(10,2) | Registro de la sesión pactada. Estados: `PROGRAMADA`, `CONFIRMADA`, `REALIZADA`, `CANCELADA`, `INASISTENCIA`. |
| `agenda_teleconsulta` | `id`<br>`cita_id`<br>`sala_id`<br>`jwt_room_token`<br>`hora_inicio_real`<br>`hora_fin_real`<br>`duracion_segundos` | UUID (PK)<br>UUID (FK Cita) UNIQUE<br>Varchar(150)<br>Text<br>DateTime<br>DateTime<br>Integer | Parámetros de conexión segura e historial de duración de la sesión virtual Jitsi Meet. |
| `agenda_alerta` | `id`<br>`paciente_id`<br>`tipo`<br>`severidad`<br>`descripcion`<br>`resuelta`<br>`fecha_creacion` | UUID (PK)<br>UUID (FK Paciente)<br>Varchar(50)<br>Varchar(20)<br>Text<br>Boolean<br>DateTime | Alertas preventivas tempranas por inasistencias consecutivas o riesgo de deserción terapéutica. |"""

def update_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace Use Case Diagram in Sprint 1
    # Find from "#### Diagrama de Casos de Uso del Sprint 1" up to "<br>\n\n#### Diagrama de Clases"
    cu_pattern = r'#### Diagrama de Casos de Uso del Sprint 1.*?(?=(?:<br>\s*\n+#### Diagrama de Clases))'
    if re.search(cu_pattern, content, flags=re.DOTALL):
        content = re.sub(cu_pattern, CU_DIAGRAM_MD + "\n\n", content, flags=re.DOTALL)
        print(f"[{path}] Casos de Uso updated.")
    else:
        print(f"[{path}] Casos de Uso pattern NOT found.")

    # 2. Replace Class Diagram in Sprint 1
    # Find from "#### Diagrama de Clases del Sprint 1" up to "<br>\n\n#### Diagrama de Actividad: Proceso de Reserva"
    class_pattern = r'#### Diagrama de Clases del Sprint 1.*?(?=(?:<br>\s*\n+#### Diagrama de Actividad: Proceso de Reserva))'
    if re.search(class_pattern, content, flags=re.DOTALL):
        content = re.sub(class_pattern, CLASS_DIAGRAM_MD + "\n\n", content, flags=re.DOTALL)
        print(f"[{path}] Diagrama de Clases updated.")
    else:
        print(f"[{path}] Diagrama de Clases pattern NOT found.")

    # 3. Replace 3-Layer Architecture Diagram in Sprint 1
    # Find from "**Código PlantText / PlantUML (Diagrama de Arquitectura de 3 Capas - Sprint 1):**" up to "<br>\n\n#### Diagrama de Despliegue"
    arch_pattern = r'\*\*Código PlantText / PlantUML \(Diagrama de Arquitectura de 3 Capas - Sprint 1\):\*\*.*?(?=(?:<br>\s*\n+#### Diagrama de Despliegue))'
    if re.search(arch_pattern, content, flags=re.DOTALL):
        content = re.sub(arch_pattern, ARCH_DIAGRAM_MD + "\n\n", content, flags=re.DOTALL)
        print(f"[{path}] Arquitectura 3 Capas updated.")
    else:
        print(f"[{path}] Arquitectura 3 Capas pattern NOT found.")

    # 4. Replace Data Design (Data Dictionary) in Sprint 1
    # Find from "#### 4.2.1.2 Diseño de Datos" up to "#### 4.2.1.3 Diseño de la Lógica de Negocio"
    data_pattern = r'#### 4\.2\.1\.2 Diseño de Datos.*?(?=(?:---\s*\n+#### 4\.2\.1\.3 Diseño de la Lógica de Negocio))'
    if re.search(data_pattern, content, flags=re.DOTALL):
        content = re.sub(data_pattern, DATA_DESIGN_MD + "\n\n", content, flags=re.DOTALL)
        print(f"[{path}] Diseño de Datos updated.")
    else:
        print(f"[{path}] Diseño de Datos pattern NOT found.")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"File {path} written successfully.\n")

if __name__ == '__main__':
    update_file('documentacion/intento.md')
    update_file('documentacion/sprint1.md')
