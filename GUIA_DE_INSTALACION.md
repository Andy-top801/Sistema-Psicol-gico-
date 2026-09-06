# 🚀 Guía Definitiva de Instalación (SIGEPSI)
**De 0 a 100: Cómo levantar el entorno completo en tu máquina local.**

Esta guía está diseñada para que cualquier desarrollador pueda descargar el repositorio y poner a funcionar el sistema en menos de 10 minutos.

---

## 🛠️ 0. Requisitos Previos
Antes de empezar, asegúrate de tener instalados los siguientes programas:
1. **Python** (versión 3.10 o superior)
2. **Node.js** (versión 18 o superior)
3. **Angular CLI** (instálalo globalmente con: `npm install -g @angular/cli`)
4. **PostgreSQL / pgAdmin** (versión 14 o superior)
5. **Flutter SDK** (solo si vas a correr la app móvil — ver sección 4)

---

## 📥 0.5 Descargar el Código (Git)
Si eres un desarrollador nuevo en el equipo:
1. Abre tu terminal.
2. Ejecuta el comando para clonar:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd SIGEPSI
   ```

**💡 Nota para desarrolladores actuales (Ej. Equipo Móvil):**
Si ya tienes el repositorio clonado en tu máquina, simplemente actualiza tu rama a la última versión ejecutando:
```bash
git pull
```
*(Asegúrate de reemplazar `<URL_DEL_REPOSITORIO>` con el enlace real de GitHub/GitLab del proyecto).*

---

## 🐘 1. Preparar la Base de Datos (pgAdmin)
1. Abre tu pgAdmin y conéctate a tu servidor local.
2. Haz clic derecho en *Databases* -> *Create* -> *Database...*
3. En el nombre de la base de datos escribe **EXACTAMENTE**: `sigepsi_db`.
4. Guarda y cierra. No tienes que crear ninguna tabla a mano.

---

## ⚙️ 2. Levantar el BACKEND (Django)

Abre una terminal y dirígete a la carpeta `BACKEND`:
```bash
cd BACKEND
```

**A. Variables de Entorno:**
1. Haz una copia del archivo `.env.example` y renómbralo a `.env`.
2. Ábrelo y cambia el valor de `TU_CONTRASEÑA_DE_POSTGRES` por la contraseña que usas en tu pgAdmin.
3. **Configuración de Correos (Sprint 0):** Para que el sistema de "Olvidar Contraseña" te envíe correos reales, añade estas líneas al final de tu `.env` (debes generar una "Contraseña de aplicación" desde la Seguridad de tu cuenta de Google, NO uses tu contraseña personal):
   ```env
   EMAIL_HOST_USER=tu_correo@gmail.com
   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion_de_16_digitos
   ```

**B. Entorno Virtual y Dependencias:**
Crea una "burbuja" de Python para instalar las librerías del proyecto sin afectar tu PC:
```bash
python -m venv venv
```
Activa el entorno:
*   En Windows: `venv\Scripts\activate`
*   En Mac/Linux: `source venv/bin/activate`

Instala las librerías:
```bash
pip install -r requirements.txt
```

**C. Migrar Tablas e Inicializar Datos:**
Si estás en Windows, puedes simplemente hacer **doble clic en el archivo `migrar_bd.bat`**. 
O si prefieres la consola, ejecuta:
```bash
python manage.py makemigrations
python manage.py migrate_schemas --shared
```
*(Si revisas tu pgAdmin ahora, verás que aparecieron 17 tablas automáticamente).*

Ahora, crea el usuario Administrador y la Clínica global ejecutando:
```bash
python manage.py init_system
```

Luego, carga los datos del Sprint 0 (Roles, Permisos y configuraciones):
```bash
python -c "exec(open('crear_datos_prueba.py', encoding='utf-8').read())"
```

**D. Iniciar el Servidor:**
```bash
python manage.py runserver
```
Déjalo corriendo. El backend ahora vive en `http://localhost:8000`.

---

## 🎨 3. Levantar el FRONTEND (Angular)

Abre **una nueva pestaña en tu terminal** (no cierres la de Django) y dirígete a la carpeta `FRONTEND`:
```bash
cd FRONTEND
```

Instala las dependencias de Node:
```bash
npm install
```

Levanta el servidor de la interfaz:
```bash
npm start
```
(O puedes usar `ng serve`). El frontend ahora vive en `http://localhost:4200`.

---

## 📱 4. Levantar el MOBILE (Flutter)

El proyecto móvil puede ejecutarse tanto en dispositivos físicos/emuladores como directamente en tu navegador web (**sin necesidad de conectar un celular ni configurar emuladores**). Esto es ideal para pruebas rápidas de interfaz y de conexión con la base de datos local.

Abre **una nueva pestaña en tu terminal** (deja Django corriendo) y dirígete a la carpeta `MOBILE`:
```bash
cd MOBILE
```

Instala las dependencias de Flutter:
```bash
flutter pub get
```

### 💻 Opción A: Pruebas rápidas en el Navegador Web (Recomendado sin celular)
Puedes ejecutar la aplicación móvil directamente en Chrome o Edge instalados en tu PC:

1. Corre la aplicación indicando la dirección de la clínica local:
   ```bash
   flutter run --dart-define=API_BASE_URL=http://sanamente.localhost:8000/api
   ```
2. La consola te mostrará una lista de dispositivos disponibles. Elige el número de **Chrome** o **Edge**.
3. El navegador se abrirá mostrando la aplicación móvil. Al estar en la misma computadora, las solicitudes a `sanamente.localhost` se comunicarán directamente con el Backend de Django sin configuraciones adicionales.

### 📱 Opción B: Ejecutar en Emulador o Dispositivo Físico
Si deseas ver cómo funciona en un entorno móvil real:
- **Emulador Android:** `sanamente.localhost` no resuelve directamente dentro de la red del emulador. Debes redireccionar el puerto ejecutando `adb reverse tcp:8000 tcp:8000` en tu consola, o correr la aplicación apuntando a la IP especial del emulador:
  ```bash
  flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api
  ```
- **Simulador iOS (Mac):** Resuelve `sanamente.localhost` por defecto:
  ```bash
  flutter run --dart-define=API_BASE_URL=http://sanamente.localhost:8000/api
  ```

---

### 🧪 4.5 Pruebas Locales (Flujo de "Olvidó su contraseña")
Para probar el restablecimiento de contraseñas de manera local sin servidores de correo externos:
1. Abre tu navegador con la aplicación móvil (Opción A).
2. Ve a *"Olvidó su contraseña"* e ingresa un correo de prueba registrado (por ejemplo: `condoridiaz2005@gmail.com`).
3. Presiona *"Enviar código"*.
4. **Obtener el código:** Ve a la terminal donde dejaste corriendo el backend de Django (`python manage.py runserver`). Verás el texto del correo electrónico impreso en la consola con una línea como esta:
   `Tu código de verificación (válido por 5 minutos): ZTQ4NDZmNDUt...`
5. **Copia el código completo** (si se divide en dos líneas debido al ancho de la terminal, únelas eliminando el signo `=` al final de la primera línea y cualquier espacio en blanco).
6. Pega el código en la pantalla de verificación y avanza para establecer tu nueva contraseña.

Para correr los tests unitarios y de integración de la app móvil:
```bash
flutter test
```

---

## 🧪 5. Probar el Sistema
Con el Backend y el Frontend corriendo simultáneamente:
1. Abre tu navegador web favorito.
2. Ingresa a la URL: **[http://localhost:4200/login](http://localhost:4200/login)**
3. Inicia sesión con las credenciales maestras:
   *   **Correo:** `admin@sigepsi.com`
   *   **Contraseña:** `Sigepsi2026!`

4. **Probar el Flujo de "Olvidar Contraseña":** 
   Ve a la pantalla de login, presiona el botón de recuperar contraseña e ingresa tu correo configurado. Recibirás un email real con un botón de acceso seguro que te redirigirá automáticamente a nuestra nueva interfaz de **"Crear Nueva Contraseña"**.

¡Listo! Si ves el mensaje de acceso exitoso, significa que el entorno Multi-Tenant, la API, JWT, la base de datos y la vista gráfica están perfectamente conectados.
