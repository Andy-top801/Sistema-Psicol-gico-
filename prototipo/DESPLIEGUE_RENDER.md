# 🚀 Guía Completa de Despliegue en Render con Docker — SIGEPSI

Esta guía explica paso a paso cómo desplegar la plataforma **SIGEPSI** (Backend Django Multi-Tenant + Base de Datos PostgreSQL + Frontend Angular 17 Nginx) en **[Render](https://render.com)** utilizando contenedores **Docker**.

---

## 🏗️ 1. Arquitectura de Despliegue

```
                                      Internet
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
       ┌─────────────────────────┐               ┌─────────────────────────┐
       │   Frontend Web Service  │               │   Backend Web Service   │
       │     (Angular 17 SPA     │               │     (Django REST +      │
       │     + Nginx Alpine)     │               │      Gunicorn 21)       │
       │  sigepsi-frontend.onrender  │           │   sigepsi-backend.onrender  │
       └────────────┬────────────┘               └────────────┬────────────┘
                    │                                         │
                    │ /api/ (Proxy Inverso Nginx)             │ ORM django-tenants
                    └────────────────────────────────────────►│
                                                              ▼
                                                 ┌─────────────────────────┐
                                                 │   Render PostgreSQL DB  │
                                                 │      (Multi-Tenant      │
                                                 │    Esquemas Aislados)   │
                                                 └─────────────────────────┘
```

---

## ⚡ 2. Método Rápido: Despliegue con Blueprint (`render.yaml`)

Render incluye soporte nativo para **Infrastructure as Code (IaC)** mediante el archivo `render.yaml` incluido en la raíz del repositorio.

### Pasos:

1. **Subir el código a GitHub / GitLab**:
   Asegúrate de que tus últimos commits (incluyendo los `Dockerfile`, `entrypoint.sh` y `render.yaml`) estén en la rama principal (`main` o `master`).

2. **Acceder a Render**:
   - Inicia sesión en **[dashboard.render.com](https://dashboard.render.com/)**.

3. **Crear Blueprint**:
   - En el Dashboard de Render, haz clic en **New +** y selecciona **Blueprint**.
   - Conecta tu repositorio de GitHub `PROYECTO_GRUPAL_OFI`.
   - Render detectará automáticamente el archivo `render.yaml`.

4. **Aprobar y Desplegar**:
   - Render mostrará el desglose de los 3 recursos que se crearán:
     - 🗄️ **Base de datos:** `sigepsi-postgres` (PostgreSQL 16)
     - ⚙️ **Backend:** `sigepsi-backend` (Docker)
     - 💻 **Frontend:** `sigepsi-frontend` (Docker con Nginx)
   - Haz clic en **Apply**.
   - ¡Listo! Render creará la base de datos, compilará las imágenes de Docker, ejecutará las migraciones y desplegará los servicios.

---

## 🛠️ 3. Método Manual: Creación Servicio por Servicio en Render

Si prefieres configurar cada componente paso a paso desde la interfaz de Render:

### Paso 1: Crear la Base de Datos PostgreSQL
1. En Render Dashboard, clic en **New +** → **PostgreSQL**.
2. **Name:** `sigepsi-postgres`
3. **Database:** `sigepsi_db`
4. **User:** `sigepsi_user`
5. **Region:** `Oregon (US West)` (o la más cercana)
6. **Plan:** `Free`
7. Clic en **Create Database**.
8. Una vez creada, copia la **Internal Database URL** (o *External Database URL*).

---

### Paso 2: Crear el Web Service del Backend (Django)
1. Clic en **New +** → **Web Service**.
2. Selecciona tu repositorio de GitHub.
3. Configuración:
   - **Name:** `sigepsi-backend`
   - **Region:** Misma región que la base de datos (`Oregon`)
   - **Branch:** `main`
   - **Root Directory:** `prototipo/backend`
   - **Runtime:** `Docker`
   - **Dockerfile Path:** `Dockerfile` (o `./Dockerfile`)
   - **Plan:** `Free`
4. En **Environment Variables**, añade:
   | Variable | Valor | Descripción |
   |---|---|---|
   | `DATABASE_URL` | *(Pegar la Internal Database URL de Render)* | Conexión Postgres |
   | `DB_SSL_REQUIRE` | `true` | Exigir SSL en Render |
   | `DJANGO_DEBUG` | `False` | Modo producción |
   | `DJANGO_SECRET_KEY` | *(Generar clave segura de 50 caracteres)* | Clave criptográfica |
   | `DJANGO_ALLOWED_HOSTS` | `*` | O tu dominio en Render |
   | `PORT` | `10000` | Puerto HTTP |
5. Clic en **Create Web Service**.
6. El script `entrypoint.sh` se encargará de:
   - Esperar la disponibilidad de PostgreSQL.
   - Ejecutar `migrate_schemas` (esquema public y tenants).
   - Sembrar el tenant `public` y el SuperAdmin `beto.caleb.delgado.rojas@gmail.com`.
   - Sembrar especialidades clínicas, psicólogos y pacientes demo.
   - Recopilar estáticos (`collectstatic`) con WhiteNoise.
   - Iniciar Gunicorn en el puerto 10000.
7. Guarda la URL pública del backend (ej: `https://sigepsi-backend.onrender.com`).

---

### Paso 3: Crear el Web Service del Frontend (Angular 17 + Nginx)
1. Clic en **New +** → **Web Service**.
2. Selecciona tu repositorio de GitHub.
3. Configuración:
   - **Name:** `sigepsi-frontend`
   - **Region:** Misma región (`Oregon`)
   - **Branch:** `main`
   - **Root Directory:** `prototipo/web`
   - **Runtime:** `Docker`
   - **Dockerfile Path:** `Dockerfile`
   - **Plan:** `Free`
4. En **Environment Variables**, añade:
   | Variable | Valor | Descripción |
   |---|---|---|
   | `PORT` | `10000` | Puerto que espera Render |
   | `BACKEND_URL` | `https://sigepsi-backend.onrender.com` | URL pública de tu backend |
5. Clic en **Create Web Service**.
6. Nginx compilará la plantilla de proxy inverso y enrutará automáticamente `/api/` hacia el backend, evitando cualquier problema de CORS.

---

## 🐳 4. Prueba y Verificación Local con Docker Compose

Antes de desplegar en Render, puedes probar todo el entorno localmente con un solo comando:

```powershell
# Ubicarse en la carpeta prototipo
cd prototipo

# Construir y levantar todos los servicios en segundo plano
docker compose up -d --build

# Verificar que los contenedores estén corriendo y saludables
docker compose ps
```

### URLs Locales en Docker Compose:
- 🌐 **Frontend Web (Angular):** [http://localhost:4200](http://localhost:4200)
- ⚙️ **Backend API (Django):** [http://localhost:8000](http://localhost:8000)
- 🗄️ **Base de Datos (PostgreSQL):** `localhost:5432`

### Ver logs en tiempo real:
```powershell
docker compose logs -f backend
docker compose logs -f frontend
```

### Detener el entorno local:
```powershell
docker compose down
```

---

## 🔐 5. Credenciales Iniciales en Producción

Una vez finalizado el despliegue en Render, puedes ingresar al sistema con las credenciales sembradas automáticamente:

| Rol | Correo Electrónico | Contraseña | Contexto |
|---|---|---|---|
| **SuperAdmin Global** | `beto.caleb.delgado.rojas@gmail.com` | `Admin1234*` | Plataforma Global / Esquema `public` |
| **Admin Centro Esperanza** | `admin@centroesperanza.com` | `Admin1234*` | Centro Esperanza (`centro_esperanza`) |
| **Psicólogo (Carlos)** | `carlos.mendoza@centroesperanza.com` | `Psicologo123*` | Centro Esperanza (`centro_esperanza`) |
| **Recepcionista** | `recepcion@centroesperanza.com` | `Recep1234*` | Centro Esperanza (`centro_esperanza`) |

---

## 💡 6. Consideraciones y Buenas Prácticas en Render (Plan Free)

1. **Suspensión por Inactividad (*Cold Start*)**:
   - En el plan Free de Render, si un servicio no recibe peticiones durante 15 minutos entra en modo "hibernación".
   - La primera petición después de la suspensión puede tardar ~30-40 segundos mientras el contenedor arranca. Esto es normal en el tier gratuito de Render.
2. **Persistencia de Base de Datos**:
   - Las bases de datos PostgreSQL en el plan Free de Render tienen una vigencia de 30 o 90 días dependiendo de las políticas actuales de Render. Para producción permanente, se recomienda el plan Starter o una base de datos externa (ej. Neon o Supabase).
3. **Certificados SSL Automáticos**:
   - Render gestiona automáticamente los certificados HTTPS (Let's Encrypt) para todos tus subdominios `*.onrender.com`.
4. **Proxy Inverso Nginx**:
   - Gracias a la configuración en `nginx.conf.template`, el frontend y el backend parecen estar en el mismo dominio para el navegador, eliminando errores de cabeceras CORS en navegadores estrictos (Safari, Chrome Mobile).
