# Explicación de la Arquitectura del Backend (SIGEPSI)

El proyecto Backend está construido utilizando **Django y Django REST Framework**, estructurado bajo un modelo de arquitectura limpia y mejores prácticas para soportar escalabilidad y **Multi-Tenancy** (múltiples clínicas en la misma base de datos).

A continuación se detalla el contenido de la carpeta `BACKEND`:

## 1. 📁 Carpeta `sigepsi/` (El núcleo del proyecto)
Esta es la carpeta principal de configuración de todo el backend.
*   **`settings.py`**: Contiene la configuración global del proyecto. Aquí se definen la conexión a la base de datos PostgreSQL, la configuración del esquema Multi-Tenant (`django-tenants`), las aplicaciones instaladas, las políticas de CORS (para permitir peticiones desde Angular/Flutter) y los parámetros de seguridad para JWT.
*   **`urls.py`**: Funciona como el enrutador maestro. Registra los endpoints principales del sistema, como `/api/users/`, delegando las rutas específicas a cada módulo (app).
*   **`wsgi.py` / `asgi.py`**: Archivos de interfaz para desplegar la aplicación en servidores de producción.

## 2. 📁 Carpeta `apps/` (Módulos del Sistema)
Esta carpeta centraliza todos los módulos del sistema (los "Paquetes" o Casos de Uso). Mantener las aplicaciones aquí adentro asegura un directorio raíz limpio. Actualmente contiene:
*   **`tenants/`**: Gestiona la arquitectura **Multi-Tenant**. Incluye los modelos `Centro` (que representa a cada clínica) y `Dominio`. Se encarga de aislar la información para que cada centro vea únicamente su propia base de datos, manteniendo un esquema `public` para la administración general.
*   **`users/`**: Administra la seguridad, autenticación y gestión de usuarios. Aquí se ha sobrescrito el modelo nativo de Django para utilizar el correo electrónico como identificador en lugar de un nombre de usuario. También contiene los modelos de `Rol` y `Permiso`, además del archivo `urls.py` encargado de procesar el inicio de sesión (`/auth/login/`) para emitir los tokens JWT, el registro de pacientes desde la app móvil (`/auth/register/`, CU27) y el perfil del usuario autenticado (`/me/`).

## 3. 📄 Archivo `manage.py`
Es el script de utilidad principal de Django. Se utiliza desde la línea de comandos para realizar tareas administrativas, tales como iniciar el servidor de desarrollo (`runserver`), procesar migraciones (`makemigrations`, `migrate`), o crear superusuarios.

## 4. 📄 Archivo `.env` (Variables de Entorno)
Este archivo gestiona las configuraciones sensibles y secretas del sistema. Almacena credenciales de la base de datos (usuario, contraseña, puerto) y la clave secreta de Django (`SECRET_KEY`). Al usar este archivo, garantizamos que las credenciales no queden expuestas en el código fuente.

## 5. 📁 Carpeta `venv/` (Entorno Virtual)
Es un entorno aislado de Python donde residen todas las dependencias y librerías del proyecto (como Django, Psycopg2, djangorestframework-simplejwt, etc.). Esto evita conflictos de versiones con otros proyectos de Python instalados en el sistema operativo.

---
*Este documento detalla la estructura base que nos permitirá integrar progresivamente los 6 paquetes funcionales del sistema (Seguridad, Gestión Clínica, Agenda, Formularios, IA y Reportes) dentro de la carpeta `apps/`.*

---

## 🛠️ Guía de Instalación para Nuevos Desarrolladores (Git)

Si acabas de clonar este repositorio, sigue estos pasos EXACTOS para poder correr el proyecto en tu máquina local y que quede exactamente igual a la base de datos de producción/pgAdmin original.

### Paso 1: Variables de Entorno (IMPORTANTE)
El archivo `.env` original **NO se sube a Git por seguridad**. 
1. Crea un archivo llamado `.env` en la raíz de la carpeta `BACKEND/`.
2. Copia todo el contenido del archivo `.env.example` y pégalo en tu nuevo `.env`.
3. Reemplaza `TU_CONTRASEÑA_DE_POSTGRES` por la contraseña de tu propio servidor local de PostgreSQL.

### Paso 2: Base de Datos en pgAdmin
Debes tener instalado PostgreSQL (pgAdmin).
1. Abre pgAdmin.
2. Crea una base de datos vacía que se llame **EXACTAMENTE**: `sigepsi_db`.

### Paso 3: Instalar Dependencias
Abre una terminal dentro de la carpeta `BACKEND/` y crea el entorno virtual:
```bash
python -m venv venv
```
Activa el entorno virtual:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

Instala las librerías:
```bash
pip install -r requirements.txt
```

### Paso 4: Migraciones (Arquitectura Multi-Tenant)
Debido a que usamos `django-tenants`, el comando de migración es especial. Ejecuta esto para construir las 17 tablas automáticas en el esquema `public`:
```bash
python manage.py migrate_schemas --shared
```

### Paso 5: Inicializar Sistema (Crear Superusuario)
Django no crea un usuario por defecto mágicamente. Para eso, he creado un script interno (que sí se sube a Git) que prepara la configuración base y crea tu administrador:
```bash
python manage.py init_system
```
Esto creará el Tenant `public` y el usuario **admin@sigepsi.com** con clave **admin123**.

### Paso 6: Correr el servidor
Ya estás listo para levantar el servidor:
```bash
python manage.py runserver
```
Si todo salió bien, el backend estará escuchando en `http://localhost:8000`.
