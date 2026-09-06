# Paquete 1 — Administración, Seguridad y Multi-Tenant

Según `CONTEXTO_PROYECTO_SIGEPSI.md` (sección 3.10), este paquete agrupa **CU1, CU2, CU3, CU4, CU5 y CU27**. En la app móvil solo dos de esos casos de uso aplican (los demás son exclusivamente Web: gestión de centros, usuarios, roles y auditoría — ver `apps.tenants`/`apps.users` en el backend). El paquete es una única unidad, igual que en `FRONTEND/src/app/modules/paquete1_admin_seguridad/` (`components/`, `services/`): las carpetas se organizan por **tipo**, no por caso de uso — un mismo `services/`, por ejemplo, contiene el código de los distintos CU que este paquete cubre.

```
paquete1_admin_seguridad/
  models/      usuario.dart, auth_tokens.dart
  services/    auth_service.dart, password_reset_service.dart
  providers/   auth_provider.dart
  screens/     login_screen.dart, register_screen.dart, forgot_password_screen.dart, reset_password_screen.dart
  widgets/     auth_header.dart, auth_text_field.dart, gradient_button.dart
```

## Qué caso de uso implementa cada archivo

| Archivo | Caso de Uso | Historias de Usuario |
|---|---|---|
| `models/usuario.dart`, `models/auth_tokens.dart` | CU2 | HU-02 |
| `services/auth_service.dart` | CU2 — Gestionar inicio de sesión y autenticación | HU-01, HU-02, HU-09 |
| `services/password_reset_service.dart` | CU27 — Recuperar contraseña o credenciales de acceso | HU-10 / RF-31 |
| `providers/auth_provider.dart` | CU2 (estado de sesión observable) | HU-02 |
| `screens/login_screen.dart`, `screens/register_screen.dart` | CU2 | HU-01, HU-02 |
| `screens/forgot_password_screen.dart`, `screens/reset_password_screen.dart` | CU27 | HU-10 |
| `widgets/*.dart` | Compartido — marca visual usada por las pantallas de ambos CU, no pertenece a un CU específico | — |

`password_reset_service.dart` es una clase separada de `auth_service.dart` (no un método más ahí adentro) porque CU27 es un caso de uso independiente de CU2 — no requiere sesión iniciada y tiene su propio ciclo (solicitar código → confirmar). Mantenerlas separadas es una decisión de diseño (una responsabilidad por clase), no una fragmentación por carpeta.

## Pendiente en este paquete

CU1, CU3, CU4, CU5 (gestión de centros, usuarios, roles, auditoría) son exclusivamente Web según el alcance del proyecto — no aplican a la app móvil.
