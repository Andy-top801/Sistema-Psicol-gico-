# Diagramas de Comunicación (UML) - Sprint 0

A continuación se presentan los diagramas de comunicación utilizando la notación visual requerida (Frontera, Control, Entidad), pero esta vez **especificando claramente a qué tecnología pertenece cada capa** y manteniendo **todos los pasos y flujos fluidos** de nuestra arquitectura real sin omitir detalles técnicos.

## Entorno Web y Móvil compartidos

### CU2 - Gestionar inicio de sesión y autenticación

```plantuml
@startuml
skinparam style strictuml

actor "Usuario" as U
boundary "IU_Login\n(Angular / Dart)" as IU
control "CTR_Auth\n(Django)" as CTR
entity "CE_Usuario\n(PostgreSQL)" as CE

U -right-> IU : +1: Ingresa email y password
IU -right-> CTR : +2: POST /api/login/ (email, password)
CTR -right-> CE : +3: select_where(email)
CE -left-> CTR : +4: Retorna Hash para validación
CTR -left-> IU : +5: 200 OK (JWT Access y Refresh)
IU -right-> CTR : +6: GET /api/users/me/ (Envia Token)
CTR -left-> IU : +7: 200 OK (Perfil, Roles, Tenant)
IU -left-> U : +8: Redirige al Dashboard principal
@enduml
```

### CU27 - Recuperar contraseña o credenciales de acceso

```plantuml
@startuml
skinparam style strictuml

actor "Usuario" as U
boundary "IU_Recuperacion\n(Angular / Dart)" as IU
control "CTR_PasswordReset\n(Django)" as CTR
entity "CE_Usuario\n(PostgreSQL)" as CE
control "Servidor_Email" as Mail

U -right-> IU : +1: Solicita recuperación(email)
IU -right-> CTR : +2: POST /password-reset/ (email)
CTR -right-> CE : +3: select_where(email)
CE -left-> CTR : +4: Usuario validado
CTR -down-> Mail : +5: Enviar correo con código
CTR -left-> IU : +6: 200 OK (Confirmación)

U -right-> IU : +7: Ingresa código y nueva contraseña
IU -right-> CTR : +8: POST /password-reset/confirm/
CTR -right-> CE : +9: Actualiza(password)
CE -left-> CTR : +10: Éxito en BD
CTR -left-> IU : +11: 200 OK (Contraseña cambiada)
IU -left-> U : +12: Redirigir al Login
@enduml
```

## Exclusivos del Entorno Web (Administración)

### CU1 - Gestionar centros psicológicos y configuración Multi-Tenant

```plantuml
@startuml
skinparam style strictuml

actor "SuperAdministrador" as SA
boundary "IU_FormularioCentro\n(Angular)" as IU
control "CTR_TenantService\n(Django)" as CTR
entity "CE_Tenant_y_Dominio\n(PostgreSQL)" as CE

SA -right-> IU : +1: Ingresar datos del nuevo Centro
IU -right-> CTR : +2: POST /api/tenants/ (datos)
CTR -right-> CE : +3: Valida disponibilidad de Dominio/Slug
CE -left-> CTR : +4: Dominio disponible
CTR -right-> CE : +5: insert(Tenant, Dominio)
CE -left-> CTR : +6: Registros creados
CTR -right-> CE : +7: CREATE SCHEMA y Migraciones
CE -left-> CTR : +8: Esquema creado
CTR -left-> IU : +9: 201 Created
IU -left-> SA : +10: Mostrar confirmación de Alta
@enduml
```

### CU3 - Gestionar usuarios

```plantuml
@startuml
skinparam style strictuml

actor "Admin del Centro" as AC
boundary "IU_GestionUsuarios\n(Angular)" as IU
control "CTR_MiddlewareTenant\n(Django)" as Mid
entity "CE_Tenant\n(Esquema Public)" as CET
control "CTR_UsuarioService\n(Django)" as CTR
entity "CE_Usuario\n(Esquema Tenant)" as CEU

AC -right-> IU : +1: Llenar formulario de nuevo usuario
IU -right-> Mid : +2: POST /api/users/ (Host)
Mid -right-> CET : +3: Identifica Tenant por URL
CET -left-> Mid : +4: Fija el contexto de BD
Mid -down-> CTR : +5: Enruta la petición
CTR -right-> CEU : +6: Valida que email no exista
CEU -left-> CTR : +7: Email disponible
CTR -right-> CEU : +8: insert(Usuario) en esquema local
CEU -left-> CTR : +9: Usuario creado exitosamente
CTR -up-> Mid : +10: 201 Created
Mid -left-> IU : +11: Retorna respuesta HTTP
IU -left-> AC : +12: Mostrar confirmación
@enduml
```

### CU4 - Gestionar roles y permisos

```plantuml
@startuml
skinparam style strictuml

actor "Admin del Centro" as AC
boundary "IU_AsignacionRoles\n(Angular)" as IU
control "CTR_RolesService\n(Django)" as CTR
entity "CE_Rol_y_Usuario\n(PostgreSQL)" as CE

AC -right-> IU : +1: Selecciona usuario y nuevo rol
IU -right-> CTR : +2: PUT /api/users/{id}/roles/
CTR -right-> CE : +3: Verifica validez del Rol
CE -left-> CTR : +4: Rol existente
CTR -right-> CE : +5: update_relacion(Usuario, Rol)
CE -left-> CTR : +6: Base de datos actualizada
CTR -left-> IU : +7: 200 OK
IU -left-> AC : +8: Mostrar éxito en pantalla
@enduml
```
