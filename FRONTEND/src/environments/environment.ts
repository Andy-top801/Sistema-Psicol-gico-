/**
 * Configuración de producción.
 *
 * `apiBase` se deriva del host del navegador para soportar multi-tenant por
 * subdominio: `centro.sigepsi.app` → API en el mismo origen. En producción se
 * asume la API detrás de un proxy inverso en el mismo host (sin puerto).
 */
export const environment = {
  production: true,
  useMockData: false,
  apiBase: `${window.location.protocol}//${window.location.host}`,
  apiPrefix: '/api',
};
