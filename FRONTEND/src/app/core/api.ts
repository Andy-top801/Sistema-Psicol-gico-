import { environment } from '../../environments/environment';

/**
 * Construye una URL absoluta contra la API a partir de una ruta relativa.
 * `apiUrl('users/citas/')` → `http://<host>:8000/api/users/citas/`
 */
export function apiUrl(path: string): string {
  const clean = path.replace(/^\/+/, '');
  return `${environment.apiBase}${environment.apiPrefix}/${clean}`;
}

/** Rutas de la API centralizadas (evita strings mágicos por servicio). */
export const API = {
  // Autenticación / cuenta
  login: 'users/auth/login/',
  refresh: 'users/auth/refresh/',
  me: 'users/me/',
  register: 'users/auth/register/',
  passwordResetRequest: 'users/auth/password-reset/request/',
  passwordResetConfirm: 'users/auth/password-reset/confirm/',
  passwordResetVerify: 'users/auth/password-reset-verify/',

  // Recursos
  usuarios: 'users/usuarios/',
  roles: 'users/roles/',
  permisos: 'users/permisos/',
  especialidades: 'users/especialidades/',
  psicologos: 'users/psicologos/',
  disponibilidades: 'users/disponibilidades-psicologo/',
  pacientes: 'users/pacientes/',
  citas: 'users/citas/',
  alertas: 'users/alertas/',
  teleconsultas: 'users/teleconsultas/',
  dashboard: 'users/dashboard/',
  tenants: 'tenants/',
} as const;
