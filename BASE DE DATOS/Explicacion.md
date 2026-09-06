# Explicación del Modelo de Base de Datos - Sprint 0 (Proyecto SIGEPSI)

## Introducción
Este documento detalla el diseño conceptual de la base de datos elaborado para el **Sprint 0** del proyecto **SIGEPSI** (Plataforma Web y Móvil de Gestión Integral de Citas, Expedientes Clínicos y Seguimiento Terapéutico para Centros de Salud Mental). El diseño ha sido cuidadosamente moldeado para ser 100% compatible con el stack tecnológico definido (PostgreSQL, Django, Django REST Framework, Angular, Flutter) y la arquitectura SaaS Multi-Tenant.

## 1. Justificación del Diseño y Compatibilidad con el Stack
¿Por qué se diseñó de esta forma? El proyecto exige una arquitectura **SaaS Multi-Tenant** (Software as a Service, Multi-empresa). Esto significa que múltiples centros psicológicos utilizarán la misma plataforma, pero su información debe estar estrictamente aislada. 

En lugar de "reinventar la rueda", el diseño conceptual se alineó milimétricamente con la arquitectura interna del framework backend (**Django**) y la librería elegida para el aislamiento de datos en PostgreSQL (**django-tenants**):
*   **django-tenants** requiere explícitamente una estructura de "Esquema Público" con una tabla principal para la identidad del inquilino y otra para sus dominios de enrutamiento. Esto justifica a nivel arquitectónico la existencia de las tablas `CENTRO` y `DOMINIO`.
*   **El motor de autenticación de Django** maneja de forma nativa los roles y permisos mediante grupos (Groups) y permisos (Permissions) vinculados al modelo de Usuario universal (`AbstractUser`). Por ello, las tablas `USUARIO`, `ROL`, `PERMISO`, y sus relaciones Muchos a Muchos (`USUARIO_ROL`, `ROL_PERMISO`) son la representación conceptual exacta de lo que el framework generará a nivel físico, garantizando que los desarrolladores trabajen a favor del entorno y no tengan conflictos o errores a futuro.

## 2. Cumplimiento del Sprint 0
Este diagrama cubre exhaustivamente todas y cada una de las Historias de Usuario (HU) definidas en el documento original para el Sprint 0:
*   **HU-01 (Registro de SuperAdministrador):** Soportado directamente por el atributo `EsSuperAdmin` en la tabla `USUARIO`.
*   **HU-02, HU-09, HU-10 (Autenticación por Tokens y Seguridad):** La tabla `USUARIO` centraliza las credenciales base. La generación y validación de JWT (JSON Web Tokens), así como los procesos transitorios de recuperación de contraseñas, serán manejados en memoria (Redis) o mediante las tablas automáticas de la librería de seguridad del API sin ensuciar la lógica de negocio de este modelo conceptual maestro.
*   **HU-03, HU-07, HU-08 (Multi-Tenant y Gestión de Centros):** Soportado por las tablas `CENTRO` y `DOMINIO`, junto con el atributo `EsActivo` de la tabla Centro que permite suspensiones.
*   **HU-04 (Configuración del centro):** Soportado aisladamente por la tabla `CONFIGURACION`.
*   **HU-05, HU-06 (Registro de usuarios, asignación de roles y permisos):** Soportado por las entidades `USUARIO`, `ROL`, `PERMISO` y sus respectivas clases asociativas.

---

## 3. Explicación Detallada de las Tablas y sus Relaciones

### CENTRO (Equivalente al "Tenant")
*   **¿Para qué sirve?** Representa a un Centro Psicológico o Consultorio que se suscribe y opera dentro de la plataforma (Ej: "Gabinete Psicológico Mente Sana").
*   **¿Por qué existe?** Es el núcleo de la arquitectura Multi-Tenant. A partir del `Id` de este registro, PostgreSQL es capaz de saber a qué entorno de datos debe apuntar para aislar por completo la información clínica y administrativa frente a otros clientes de la plataforma.

### DOMINIO
*   **¿Para qué sirve?** Guarda la URL o subdominio a través del cual los pacientes y el personal acceden a su respectivo centro (Ej: `mentesana.sigepsi.com`).
*   **¿Por qué es una tabla separada del Centro y por qué su relación es 1 a Muchos?** La librería de ruteo (`django-tenants`) está diseñada con la flexibilidad de permitir que un mismo centro pueda responder a múltiples URLs simultáneamente (por ejemplo, el subdominio genérico del sistema y, opcionalmente, un dominio ".com" propio comprado por el cliente). Al ser una relación **1 a Muchos (1:N)**, un `CENTRO` puede tener asociados varios `DOMINIOS`.

### CONFIGURACION
*   **¿Para qué sirve?** Almacena datos estéticos y públicos específicos del centro (URL de su logo, color principal para personalizar la app, dirección física, teléfono oficial).
*   **¿Por qué fue diseñada como una tabla independiente?** Principalmente por escalabilidad y limpieza técnica (Principio de Responsabilidad Única). Separar la configuración de la tabla `CENTRO` mantiene la lógica central de infraestructura separada de la lógica de negocio secundaria. Si en Sprints posteriores (ej. pagos online en el SP4) se requieren llaves de pasarelas de pago u horarios, irán a esta tabla. Su relación es estrictamente **1 a 1 (1:1)** con `CENTRO`.

### USUARIO
*   **¿Para qué sirve?** Es la entidad central de autenticación y recursos humanos. Almacena las credenciales de acceso seguras (correo, contraseña encriptada) e identidad básica de todas las personas que interactúan en la plataforma.
*   **¿Por qué fue diseñada así?** En este modelo, se agrupan todos los tipos de individuos (Recepcionista, Psicólogo, Paciente, Administrador) bajo una única entidad genérica de autenticación. La responsabilidad de determinar qué puede hacer cada uno dentro del software se delega por completo a los **Roles**. Su relación es **1 a Muchos (1:N)** con `CENTRO` (un centro tiene muchos usuarios registrados, pero cada usuario pertenece al entorno de un centro específico, garantizando que un paciente de un centro no exista en otro).

### ROL
*   **¿Para qué sirve?** Define el "puesto", "cargo" o "categoría" del usuario dentro de la plataforma (Ej: "Coordinador Clínico", "Psicólogo", "Paciente").
*   **¿Por qué existe?** Es la base fundamental para implementar un esquema RBAC (Control de Acceso Basado en Roles). En lugar de otorgar privilegios directamente al usuario (lo cual sería inmanejable), se le asigna un Rol preestablecido, simplificando drásticamente la administración de seguridad del sistema.

### PERMISO
*   **¿Para qué sirve?** Representa una acción atómica, técnica y altamente específica que el código permite ejecutar (Ej: `crear_cita`, `ver_historia_clinica_completa`, `registrar_pago`).
*   **¿Por qué existe?** Para brindar un control de seguridad microscópico. Estos permisos se agrupan dentro de los roles.

### USUARIO_ROL y ROL_PERMISO (Tablas / Clases Asociativas)
*   **¿Por qué existen estas tablas intermedias?** Las bases de datos relacionales puras no permiten registrar relaciones múltiples directas en un solo campo, requieren una tabla "puente" para lograr la normalización de datos.
*   **¿Por qué la relación es de ese tipo (Muchos a Muchos)?** 
    *   **En USUARIO_ROL:** Un usuario en el mundo real puede tener varios roles (por ejemplo, el Dr. Pérez puede ser "Psicólogo" y al mismo tiempo "Administrador de Centro"), y un rol específico (como "Paciente") evidentemente lo poseen cientos de usuarios. Esta realidad genera una cardinalidad **Muchos a Muchos (N:M)**, requiriendo esta tabla para cruzar qué usuario tiene qué rol(es) junto con su fecha de asignación.
    *   **En ROL_PERMISO:** Un rol para ser funcional necesita múltiples permisos (el Recepcionista necesita poder `ver_agenda`, `crear_cita`, `cobrar_sesion`), y un permiso popular (como `iniciar_videollamada`) puede estar autorizado para varios roles distintos (Psicólogo y Paciente). Esta naturaleza **Muchos a Muchos (N:M)** origina la segunda tabla asociativa.
