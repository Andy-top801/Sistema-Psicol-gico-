# SIGEPSI — Frontend (Angular 18)

Panel administrativo web + portal de paciente para la plataforma de gestión de
centros de salud mental. Multi-tenant **por subdominio**.

## Requisitos

- Node 18+ y npm
- Backend corriendo (ver `../BACKEND`)

## Puesta en marcha (desarrollo)

```bash
npm install
ng serve            # ya trae host 0.0.0.0 y allowedHosts: ['.localhost']
```

La API se resuelve automáticamente a partir del host del navegador
(`environment.development.ts`): al abrir `http://sanamente.localhost:4200` las
peticiones van a `http://sanamente.localhost:8000` y `django-tenants` resuelve el
esquema del centro por el `Host`.

### Subdominios en local

Chrome, Edge y Firefox resuelven `*.localhost` a `127.0.0.1` automáticamente. En
otros navegadores, añade a `C:\Windows\System32\drivers\etc\hosts`:

```
127.0.0.1  localhost sanamente.localhost norte.localhost
```

### URLs de prueba

| URL | Quién entra |
|---|---|
| `http://localhost:4200` | Superadmin de plataforma (`admin@sigepsi.com` / `admin123`) |
| `http://sanamente.localhost:4200` | Personal y pacientes de "Sanamente" (`Demo1234!`) |
| `http://norte.localhost:4200` | Personal y pacientes de "Centro Norte" (`Demo1234!`) |

Cuentas demo del centro (contraseña `Demo1234!`):
`admin@sanamente.com`, `coordinador@sanamente.com`, `recepcion@sanamente.com`,
`psicologo@sanamente.com`, `paciente@sanamente.com` (y equivalentes `@norte.com`).

## Arquitectura

- `src/app/core/` — `apiUrl`, interceptores (auth + errores), guards
  (`auth`/`role`/`public`), `ThemeService`, `TenantContextService`, modelos.
- `src/app/shared/` — `SharedModule`: `BrandLogo`, `ThemeToggle`, `NavIcon`,
  `PageHeader`, `EmptyState`.
- `src/app/layouts/` — `PublicLayout` (auth), `AdminLayout` (staff, responsive),
  `PatientLayout` (portal).
- `src/app/modules/` — `auth`, `paquete1-admin-seguridad` (panel), `paquete2/3`
  (clínica SP1), `portal` (paciente SP1).
- `src/styles.css` — sistema de diseño único: tokens en `:root` (claro por
  defecto) y `[data-theme="dark"]` + `@media (prefers-color-scheme: dark)`.
  **Regla:** los componentes usan `var(--…)`, nunca hex.
