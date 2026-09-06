# Arquitectura de la Base de Datos: Migraciones vs SQL Directo

Si acabas de ejecutar los scripts de migración y revisaste **pgAdmin**, notarás dos cosas importantes: no ejecutamos un script SQL tradicional (`.sql`) directamente en la consola de PostgreSQL, y en lugar de las 8 tablas de nuestro diseño conceptual, aparecieron **17 tablas**.

A continuación se detalla la justificación técnica de esta decisión arquitectónica.

## 1. ¿Por qué usamos Migraciones (Python) en lugar de SQL Directo en pgAdmin?

En arquitecturas modernas y, muy especialmente, en plataformas **Multi-Tenant (Múltiples Inquilinos)** como SIGEPSI, escribir sentencias `CREATE TABLE` manuales en SQL es considerado una mala práctica. Se optó por usar el **ORM (Object-Relational Mapping)** de Django por las siguientes razones de peso:

*   **Soporte Multi-Tenant Automático:** El framework que utilizamos (`django-tenants`) exige tener el control absoluto de la base de datos para poder crear "Esquemas" dinámicos. Si registramos una nueva clínica en el sistema, Django creará automáticamente un nuevo esquema y clonará todas las tablas de forma independiente. Si creáramos las tablas a mano con SQL, perderíamos esta automatización clave del proyecto.
*   **Única Fuente de Verdad (Single Source of Truth):** Toda la estructura de la base de datos está programada en código Python (dentro de los archivos `models.py`). Si en el futuro agregamos una columna nueva, modificamos el Python y el sistema altera la base de datos de manera segura sin obligarnos a recordar escribir comandos `ALTER TABLE`.
*   **Seguridad y Mantenibilidad:** El ORM previene de manera automática ataques de inyección SQL (SQL Injection).

## 2. ¿Por qué hay 17 tablas si el modelo conceptual tenía menos?

Al pasar de un **Diagrama Conceptual** al **Modelo Físico Relacional** de la base de datos, el framework crea tablas de infraestructura y tablas intermedias "invisibles" en el concepto, pero obligatorias en la práctica, para que todo funcione.

El desglose de las 17 tablas es el siguiente:

### A. Tablas de Negocio (Las que diseñamos)
Son la transcripción literal de nuestro diagrama:
1. `tenants_centro` (Clínicas de Salud Mental)
2. `tenants_dominio` (URLs o dominios de acceso)
3. `users_usuario` (Personal médico / pacientes)
4. `users_rol`
5. `users_permiso`
6. `users_configuracioncentro`

### B. Tablas Puente (Relaciones Muchos a Muchos)
En SQL, cuando existe una relación "Muchos a Muchos" (Ej: Un usuario tiene varios roles, y un rol lo tienen varios usuarios), se requiere una tabla intermedia que una las llaves foráneas. Django las crea de forma 100% automática para nosotros:
7. `users_usuario_roles` 
8. `users_rol_permisos` 
9. `users_usuario_groups` (Tabla puente de compatibilidad nativa)
10. `users_usuario_user_permissions` (Tabla puente de compatibilidad nativa)

### C. Tablas Nativas de Infraestructura
Son las tablas que el framework implementa por defecto para ahorrarnos el trabajo de programar el manejo de seguridad, sesiones y auditoría desde cero:
11. `django_migrations`: Historial de control de versiones. Registra qué actualizaciones se han aplicado a la base de datos.
12. `django_session`: Administra las sesiones activas de los usuarios en el sistema.
13. `django_admin_log`: Guarda un historial de auditoría estricto sobre quién creó, editó o eliminó registros.
14. `django_content_type`: Catálogo maestro que registra todos los modelos instalados.
15. `auth_group`
16. `auth_group_permissions`
17. `auth_permission`
*(Estas últimas tres conforman el núcleo de seguridad de Django, sobre el cual nosotros extendimos y personalizamos nuestro propio sistema de permisos para los usuarios de SIGEPSI).*
