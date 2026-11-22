# Guía Paso a Paso de Pruebas — Sprint 4 (SIGEPSI)

Esta guía explica cómo levantar el proyecto en local y probar **todas las Historias de Usuario del Sprint 4 (`HU-49` a `HU-56`)**, indicando exactamente con qué credenciales iniciar sesión, cuándo cerrar sesión para cambiar de rol o centro, y cómo moverse entre cada vista.

---

## 1. Levantar el Entorno Local

Asegúrate de tener corriendo **PostgreSQL 16** en el puerto `5433` (con las credenciales locales en `prototipo/backend/.env`).

### Terminal 1 — Backend Django (puerto `8000`)
```bash
cd prototipo/backend
./venv/bin/python manage.py runserver
```

### Terminal 2 — Frontend Angular 17 (puerto `4200`)
```bash
cd prototipo/web
npm start
```

Luego abre en tu navegador: **`http://localhost:4200/login`**

> *(Opcional)* Si deseas volver a poblar los datos históricos de 24 meses + 20 años en otro tenant distinto a `centro_esperanza` y `mentesana`, ejecuta:
> ```bash
> ./venv/bin/python manage.py seed_historico_sprint4 --tenant oasis_emocional
> ```

---

## 2. Tabla Maestra de Credenciales Demo

Para cambiar de usuario en cualquier momento: haz clic en el botón **Cerrar Sesión** (ícono de salida en la parte inferior izquierda del menú lateral) y vuelve a ingresar en `/login`.

| Rol | Centro / Contexto en Login | Correo | Contraseña | Para qué HUs sirve |
| :--- | :--- | :--- | :--- | :--- |
| **SuperAdmin** | Plataforma Global *(sin centro / `public`)* | `admin@sigepsi.com` | `Admin1234*` | `HU-55` (Suscripciones SaaS USD, Facturas, Cupos) |
| **Admin Centro** | `Centro Esperanza` (`centro_esperanza`) | `admin@centroesperanza.com` | `Admin1234*` | `HU-51`, `HU-52`, `HU-53`, `HU-54` |
| **Recepcionista** | `Centro Esperanza` (`centro_esperanza`) | `recepcion@centroesperanza.com` | `Recep1234*` | `HU-52` (Caja Clínica, Cobros, Extracto 20 años) |
| **Psicólogo (Asignado)** | `Centro Esperanza` (`centro_esperanza`) | `lucia.rios@centroesperanza.com` | `Psicologo123*` | `HU-49` (Resumen IA HITL), `HU-50`, `HU-54` (Ver su boleta) |
| **Psicólogo (Otro)** | `Centro Esperanza` (`centro_esperanza`) | `psicologo@centroesperanza.com` | `Psico1234*` | `HU-49` (Prueba de bloqueo `403` si no está asignado) |
| **Paciente** | `Centro Esperanza` (`centro_esperanza`) | `mateo.quispe@centroesperanza.com` | `Paciente123*` | `HU-52` (Su propio estado de cuenta) y `HU-53` (Bloqueo `403`) |
| **Admin Centro B** | `Mente Sana` (`mentesana`) | `admin@mentesana.com` | `Admin1234*` | `HU-56` (Validar aislamiento multi-tenant entre centros) |

---

## 3. Paso a Paso por Historia de Usuario

### HU-49 — Generación asistida de resúmenes clínicos longitudinales por IA (Híbrido + HITL)

1. **Inicia sesión** en `/login` seleccionando **Centro Esperanza** con el Psicólogo tratante:
   - Correo: `lucia.rios@centroesperanza.com` | Contraseña: `Psicologo123*`
2. En el menú lateral (**EXPEDIENTES & CLÍNICA**), haz clic en **Historias Clínicas (EHR)** (`/historias-clinicas`).
3. Haz clic en **Ver Detalle** sobre una historia clínica que tenga al menos 2 notas SOAP o evoluciones.
4. En las pestañas superiores del expediente, haz clic en la última pestaña: **Resumen Clínico IA (HITL)**.
5. Presiona **Generar Borrador IA**:
   - Verifica que aparezca el banner ámbar obligatorio **`Borrador IA — Requiere Revisión Profesional`**, el modelo utilizado (`HUGGINGFACE` o `FALLBACK_LOCAL`) y el **hash SHA-256**.
   - Verifica que **no** aparezcan datos sensibles (CI, correo ni teléfono) en el texto generado.
6. Edita libremente una línea en el cuadro de texto y haz clic en **Editar y Aprobar (HITL)**:
   - El banner cambiará a verde (**`Aprobado por Profesional (HITL)`**).
7. Haz clic en **Exportar PDF** y verifica la descarga del archivo `resumen_ia_<expediente>.pdf`.
8. **Prueba de seguridad RBAC (`403`)**:
   - Haz clic en **Cerrar Sesión** (pie del menú lateral).
   - Inicia sesión con `psicologo@centroesperanza.com` / `Psico1234*` (u otro psicólogo no asignado a ese paciente) e intenta abrir esa misma historia clínica: el sistema bloqueará el acceso y auditará el intento en `CE_AuditLog`.

---

### HU-50 y HU-51 — Detección longitudinal de riesgo/deserción y Consola de Alertas Prioritarias

1. **Cierra sesión** si estabas con otro rol e inicia sesión en **Centro Esperanza** como **Admin Centro**:
   - Correo: `admin@centroesperanza.com` | Contraseña: `Admin1234*`
2. En el menú lateral (**EXPEDIENTES & CLÍNICA**), haz clic en **Alertas de Riesgo IA** (`/alertas-riesgo-ia`).
3. Haz clic en el botón superior derecho **Ejecutar Barrido IA (CU24)**:
   - El motor evaluará a todos los pacientes del centro con las 4 señales (léxico vital, $\ge 3$ días de ánimo $\le 2$, $\ge 2$ inasistencias / $>21$ días sin cita, adherencia a tareas) y mostrará el resumen de pacientes evaluados y alertas actualizadas.
4. Navega por los tabs **Todas**, **Críticas**, **Abiertas**, **En Atención** y **Resueltas**:
   - Comprueba que las alertas **`CRITICO`** aparecen siempre arriba ordenadas por score (`0–100`) descendente, con sus chips de factores explicables.
5. Vuelve a presionar **Ejecutar Barrido IA (CU24)** y confirma que **no se duplican** las alertas ya abiertas.
6. En una alerta abierta, haz clic en **Intervenir / Gestionar**:
   - Selecciona estado **`Resuelta`**, deja la nota vacía y presiona **Guardar y Auditar en CE_AuditLog** → verifica que el sistema **bloquea** la acción exigiendo la nota de intervención clínica.
   - Escribe una nota (ej: *"Se realizó llamada de contención telefónica y se reagendó sesión de urgencia"*) y presiona **Guardar y Auditar en CE_AuditLog** → la alerta pasa a `RESUELTA` y aparece en el tab **Resueltas** con su bitácora.

---

### HU-52 — Caja Clínica en Bs., Recibo PDF y Extracto Histórico Tipo Banco (hasta 20 años)

1. **Cierra sesión** e inicia sesión en **Centro Esperanza** como **Recepcionista** (o continúa como **Admin Centro**):
   - Correo: `recepcion@centroesperanza.com` | Contraseña: `Recep1234*`
2. En el menú lateral (**FINANZAS & CAJA (Bs.)**), haz clic en **Caja y Extracto 20 Años** (`/finanzas/caja`).
3. **Probar Caja y Cobros (Pestaña 1 — `Caja y Cobros`)**:
   - Haz clic en **Sincronizar** si deseas asegurar todos los cargos de citas.
   - Selecciona un paciente con saldo pendiente (`> 0.00 Bs.`) haciendo clic en **Cobrar / Ver**.
   - **Validación de error (`400`)**: intenta cobrar `-10` o un monto mayor al saldo pendiente → verifica el mensaje de rechazo.
   - **Cobro válido**: elige el método **QR Bancario**, ingresa un monto válido (ej. `150.00`), opcionalmente una referencia (`QR-BNB-001`) y haz clic en **Confirmar Cobro y Emitir Recibo**.
   - Verifica que el `Saldo Pendiente` se descuente automáticamente y aparezca el pago en **Pagos Recientes del Paciente** con su `N° Recibo` (`REC-2026-...`).
   - Haz clic en el ícono rojo de **PDF** en la fila del recibo para descargar el comprobante oficial en `Bs.`.
4. **Probar Extracto Histórico Tipo Banco de 20 Años (Pestaña 2 — `Extracto Tipo Banco (20 Años)`)**:
   - Haz clic en el botón superior **Extracto Tipo Banco (20 Años)**.
   - Haz clic en el preset **`20 Años`** (rango `2006/2007` a `2026`) y presiona **Consultar**.
   - Verifica las 4 tarjetas superiores (`Saldo Inicial`, `Total Cargos (Debe)`, `Total Pagos (Haber)`, `Saldo Final`), la columna **Saldo Acumulado** línea por línea y los botones de paginación **Anterior / Siguiente**.
   - Prueba las 3 exportaciones masivas:
     - **PDF Multipágina** (verifica encabezados repetidos por página, numeración `Página X de Y` y tabla de Resumen Consolidado por Año al final).
     - **Excel Streaming** (abre el `.xlsx` y verifica las 2 hojas: *Extracto Histórico* y *Resumen Anual*).
     - **CSV** (descarga inmediata en streaming).
5. **Prueba de vista Paciente**:
   - **Cierra sesión** e inicia sesión en **Centro Esperanza** como **Paciente** (`mateo.quispe@centroesperanza.com` / `Paciente123*`).
   - En el menú lateral haz clic en **Mi Estado de Cuenta** (`/finanzas/caja`): verifica que solo puede ver su propia cuenta y su propio extracto (sin acceso a otros pacientes).

---

### HU-53 — Dashboard Financiero Gerencial ($\ge 2$ años) y Centro Integral de Reportes

1. **Primero valida el bloqueo RBAC** (mientras sigues logueado como Paciente `mateo.quispe@centroesperanza.com`):
   - Intenta navegar manualmente a `http://localhost:4200/finanzas/dashboard` → serás redirigido al inicio (y el API retorna `403 Forbidden`).
2. **Cierra sesión** e inicia sesión en **Centro Esperanza** como **Admin Centro**:
   - Correo: `admin@centroesperanza.com` | Contraseña: `Admin1234*`
3. En el menú lateral (**GESTIÓN ADMINISTRATIVA**), haz clic en **Dashboard Financiero (Bs.)** (`/finanzas/dashboard`).
4. Verifica los **4 KPIs principales en `Bs.`**:
   - **Ingreso Bruto Cobrado** (con variación interanual YoY %).
   - **Honorarios Profesionales** (y comisión retenida del centro).
   - **Margen Neto Real del Centro** (`Ingreso Bruto - Honorarios`, en verde esmeralda, con YoY %).
   - **Cuentas por Cobrar / Morosidad (%)**.
5. Verifica la gráfica longitudinal **Evolución Mensual (24 meses / 2 Años)** por defecto y prueba cambiar el horizonte a **`12 Meses`**, **`36 Meses`** y **`Todo el Historial`**.
6. Baja a las tablas de **Recaudación por Método de Pago** y **Rendimiento Económico por Psicólogo**.
7. En la sección inferior **Centro Integral de Reportes y Consultas (PDF / Excel / CSV)**:
   - Verifica que aparecen todas las fuentes clínicas, operativas, IA y financieras (`Citas`, `Pacientes`, `Psicólogos`, `Cobros y Pagos`, `Estado de Cuentas`, `Extracto Histórico`, `Liquidaciones`, `Alertas Riesgo IA`, `Resúmenes IA`, etc.).
   - Haz clic en **PDF**, **Excel** y **CSV** en cualquiera de los reportes para confirmar descarga directa, o en **Ver** para abrir el visor interactivo.

---

### HU-54 — Liquidación Periódica de Honorarios a Psicólogos en Bs.

1. Manteniendo sesión como **Admin Centro** (`admin@centroesperanza.com` en **Centro Esperanza**):
2. En el menú lateral (**FINANZAS & CAJA (Bs.)**), haz clic en **Liquidación Honorarios** (`/finanzas/liquidaciones`).
3. En **Calcular Nueva Liquidación**:
   - Selecciona un psicólogo, un rango de fechas que tenga sesiones `REALIZADAS` aún no liquidadas y porcentaje de comisión (ej. `30%` centro / `70%` psicólogo).
   - Haz clic en **Previsualizar** y verifica el cálculo exacto (`Monto Bruto`, `Retención Centro`, `Neto a Pagar`).
   - Haz clic en **Emitir Liquidación** → se crea en estado **`GENERADA`**.
4. **Prueba de anti-doble pago**:
   - Vuelve a presionar **Emitir Liquidación** con el mismo psicólogo y las mismas fechas → el sistema rechaza la operación indicando que no quedan sesiones pendientes de liquidar.
5. En la tabla **Historial de Liquidaciones Emitidas**:
   - Haz clic en **Pagar** en una liquidación `GENERADA`, ingresa una referencia bancaria (ej. `TRANS-BNB-2026-88`) y confirma → pasa a estado **`PAGADA`**.
   - Haz clic en **Boleta PDF** para descargar la boleta oficial.
6. **Prueba de consulta por el Psicólogo**:
   - **Cierra sesión** e inicia sesión como Psicólogo (`lucia.rios@centroesperanza.com` / `Psicologo123*`).
   - Ve a **Liquidación Honorarios** (`/finanzas/liquidaciones`): verifica que el formulario de emisión está oculto para su rol, que solo ve **sus propias liquidaciones** y que puede descargar su **Boleta PDF**.

---

### HU-55 — Consola SuperAdmin de Suscripciones SaaS, Stripe y Cupos (USD)

1. **Cierra sesión** del centro.
2. En `/login`, inicia sesión como **SuperAdmin** en modo **Plataforma Global** (sin seleccionar un centro tenant):
   - Correo: `admin@sigepsi.com` | Contraseña: `Admin1234*`
3. En el menú lateral (**GESTIÓN ADMINISTRATIVA**), haz clic en **Suscripciones SaaS (USD)** (`/suscripciones-saas`).
4. Verifica los KPIs globales en **USD**:
   - **MRR Mensual (USD)** y **ARR Estimado (USD)**.
   - **Centros Activos** (`12 / 12` centros tenant).
   - **Total Facturado (USD)** y chips de **Distribución de Planes** (`Básico`, `Pro`, `Emp`).
5. En la tabla de centros:
   - Haz clic en **Ver Facturas USD** de cualquier centro (ej. `Centro Esperanza`) → se abre el panel inferior con el historial de `FacturaSaaS` (`FAC-SAAS-2026-...`, `Stripe Session ID`, monto en USD y fecha de renovación).
   - Prueba cambiar el plan de un centro usando el selector (`Básico ($29)` / `Profesional ($59)` / `Empresarial ($99)`) y observa cómo se actualiza el MRR en tiempo real.
   - Si dejas un centro con $>3$ psicólogos activos en plan **`Básico ($29)`**, verás la alerta visual en su columna de **Cupos** y, al intentar crear un nuevo psicólogo dentro de ese centro, el backend bloqueará el alta sugiriendo actualizar a **Profesional ($59/mes)**. *(Recuerda devolverlo a `Profesional` al terminar tu prueba).*

---

### HU-56 — Certificación de Estrés, Concurrencia y Aislamiento Multi-Tenant

1. **Verificación visual rápida entre centros**:
   - Inicia sesión en **Centro Esperanza** (`admin@centroesperanza.com` / `Admin1234*`), abre `/finanzas/dashboard` y anota su Ingreso Bruto.
   - **Cierra sesión**, inicia sesión en **Mente Sana** (`admin@mentesana.com` / `Admin1234*`), abre `/finanzas/dashboard` y confirma que los montos, pacientes y extractos corresponden exclusivamente a `Mente Sana` sin mezclar registros.
2. **Certificación automatizada completa (32 peticiones concurrentes, JWT cross-tenant y benchmark 20 años / 24 meses)**:
   ```bash
   cd prototipo/backend
   ./venv/bin/python verify_sprint4.py
   ```
   Debes obtener al final:
   ```text
   [CERTIFICADO] 5/5 SUITES DEL SPRINT 4 APROBADAS AL 100%.
   ```
