import { AppRole, STAFF_ROLES } from '../core/models/user.model';

export interface NavItem {
  label: string;
  path: string;
  /** Nombre de icono (se dibuja con NavIconComponent). */
  icon: string;
  roles: AppRole[];
  /** Referencia opcional al caso de uso. */
  cu?: string;
}

/** Navegación del panel administrativo (staff). Se filtra por rol en el layout. */
export const NAV_ITEMS: NavItem[] = [
  { label: 'Panel', path: '/dashboard', icon: 'home', roles: STAFF_ROLES, cu: 'CU9' },
  { label: 'Centros', path: '/tenants', icon: 'building', roles: ['superadmin'], cu: 'CU1' },
  { label: 'Config. del centro', path: '/centro-config', icon: 'settings', roles: ['superadmin', 'admincentro'] },
  { label: 'Usuarios', path: '/users', icon: 'users', roles: ['superadmin', 'admincentro'], cu: 'CU3' },
  { label: 'Roles y permisos', path: '/roles', icon: 'shield', roles: ['superadmin', 'admincentro'], cu: 'CU4' },
  { label: 'Psicólogos', path: '/psicologos', icon: 'stethoscope', roles: ['superadmin', 'admincentro', 'coordinador'], cu: 'CU6' },
  { label: 'Pacientes', path: '/pacientes', icon: 'folder', roles: STAFF_ROLES, cu: 'CU7' },
  { label: 'Agenda y citas', path: '/citas', icon: 'calendar', roles: STAFF_ROLES, cu: 'CU11' },
  { label: 'Teleconsultas', path: '/teleconsultas', icon: 'video', roles: STAFF_ROLES, cu: 'CU13' },
  { label: 'Alertas', path: '/alertas', icon: 'alert', roles: ['superadmin', 'admincentro', 'coordinador', 'psicologo'], cu: 'CU10' },
];

/** Navegación del portal del paciente. */
export const PORTAL_NAV_ITEMS: NavItem[] = [
  { label: 'Inicio', path: '/portal', icon: 'home', roles: ['paciente'] },
  { label: 'Mis citas', path: '/portal/citas', icon: 'calendar', roles: ['paciente'], cu: 'CU11' },
  { label: 'Teleconsulta', path: '/portal/teleconsulta', icon: 'video', roles: ['paciente'], cu: 'CU13' },
  { label: 'Mi perfil', path: '/portal/perfil', icon: 'user', roles: ['paciente'] },
];
