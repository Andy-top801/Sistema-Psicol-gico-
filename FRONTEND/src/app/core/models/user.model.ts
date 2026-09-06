/** Roles canónicos del sistema (normalizados: sin acentos, minúsculas, sin espacios). */
export type AppRole =
  | 'superadmin'
  | 'admincentro'
  | 'coordinador'
  | 'psicologo'
  | 'recepcionista'
  | 'paciente'
  | 'unknown';

/** Roles del personal de un centro (acceden al panel administrativo). */
export const STAFF_ROLES: AppRole[] = [
  'superadmin',
  'admincentro',
  'coordinador',
  'psicologo',
  'recepcionista',
];

/** Precedencia para resolver el "rol principal" cuando un usuario tiene varios. */
export const ROLE_PRECEDENCE: AppRole[] = [
  'superadmin',
  'admincentro',
  'coordinador',
  'psicologo',
  'recepcionista',
  'paciente',
  'unknown',
];

/** Etiqueta legible para la UI. */
export const ROLE_LABEL: Record<AppRole, string> = {
  superadmin: 'Superadministrador',
  admincentro: 'Administrador del Centro',
  coordinador: 'Coordinador Clínico',
  psicologo: 'Psicólogo',
  recepcionista: 'Recepcionista',
  paciente: 'Paciente',
  unknown: 'Usuario',
};

/** Perfil del usuario autenticado (viene de `GET /api/users/me/`). */
export interface AppUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  roles: string[];
  is_superuser?: boolean;
  is_staff?: boolean;
  paciente_id?: string | null;
}

/** Rango de marcas diacríticas combinantes (U+0300–U+036F). */
const DIACRITICS = new RegExp('[\\u0300-\\u036f]', 'g');

/** Normaliza el nombre de un rol: sin acentos, minúsculas, sin espacios. */
export function normalizeRole(name: string): string {
  return (name || '')
    .normalize('NFD')
    .replace(DIACRITICS, '')
    .toLowerCase()
    .replace(/\s+/g, '');
}
