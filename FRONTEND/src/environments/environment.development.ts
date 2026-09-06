/**
 * Configuración de desarrollo.
 *
 * La API corre en el puerto 8000 en el mismo host que sirve el frontend, de
 * modo que al abrir `sanamente.localhost:4200` las peticiones van a
 * `sanamente.localhost:8000` y `django-tenants` (TenantMainMiddleware) resuelve
 * el schema del centro por el `Host`. En `localhost:4200` la API es
 * `localhost:8000` → schema `public` (superadmin de plataforma).
 */
export const environment = {
  production: false,
  useMockData: false,
  apiBase: `${window.location.protocol}//${window.location.hostname}:8000`,
  apiPrefix: '/api',
};
