import { Usuario } from './index';

export interface Especialidad {
  id: number;
  nombre: string;
  descripcion?: string;
}

export interface Disponibilidad {
  id?: string;
  psicologo?: string;
  dia_semana: number; // 0=Domingo, 1=Lunes, ..., 6=Sábado
  hora_inicio: string; // 'HH:MM' o 'HH:MM:SS'
  hora_fin: string;
  duracion_bloque_min: number;
  activo?: boolean;
}

export interface Psicologo {
  id: string;
  usuario: Usuario;
  numero_colegiado: string;
  biografia?: string;
  modalidad: 'PRESENCIAL' | 'VIRTUAL' | 'MIXTA';
  tarifa_base: number;
  activo: boolean;
  fecha_ingreso: string;
  especialidades: Especialidad[];
  disponibilidades?: Disponibilidad[];
}

export interface Paciente {
  id: string;
  usuario: Usuario;
  codigo_expediente: string;
  ci: string;
  fecha_nacimiento: string;
  genero: 'M' | 'F' | 'O';
  edad?: number;
  contacto_emergencia_nombre?: string;
  contacto_emergencia_telf?: string;
  tutor_legal_nombre?: string;
  tutor_legal_ci?: string;
  fecha_registro: string;
}

export interface CrearPsicologoDTO {
  email: string;
  nombre: string;
  apellido: string;
  password?: string;
  telefono?: string;
  numero_colegiado: string;
  biografia?: string;
  modalidad: 'PRESENCIAL' | 'VIRTUAL' | 'MIXTA';
  tarifa_base: number;
  especialidad_ids: number[];
}

export interface CrearPacienteDTO {
  email: string;
  nombre: string;
  apellido: string;
  password?: string;
  telefono?: string;
  ci: string;
  fecha_nacimiento: string;
  genero: 'M' | 'F' | 'O';
  contacto_emergencia_nombre?: string;
  contacto_emergencia_telf?: string;
  tutor_legal_nombre?: string;
  tutor_legal_ci?: string;
}
