export interface Usuario {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  telefono?: string;
  rol?: Rol;
  rol_detalle?: Rol;
  rol_id?: number;
  activo: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  fecha_creacion: string;
}

export interface Rol {
  id: number;
  nombre: string;
  descripcion?: string;
  permisos?: Permiso[];
  permiso_ids?: number[];
}

export interface Permiso {
  id: number;
  nombre: string;
  codigo: string;
  modulo: string;
  descripcion?: string;
}

export interface Tenant {
  id: string;
  nombre: string;
  slug: string;
  schema_name: string;
  direccion?: string;
  telefono?: string;
  email_contacto?: string;
  plan: string;
  activo: boolean;
  fecha_creacion: string;
  dominios?: Dominio[];
}

export interface Dominio {
  id: number;
  domain: string;
  is_primary: boolean;
}

export interface CentroConfig {
  id: string;
  nombre: string;
  direccion: string;
  telefono: string;
  email: string;
  logo?: string;
  horarios_atencion: Record<string, string>;
  configuracion: Record<string, any>;
  fecha_actualizacion?: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  rol: string;
  usuario: Usuario;
  tenant?: Tenant;
}

export * from './clinica.model';
export * from './agenda.model';
