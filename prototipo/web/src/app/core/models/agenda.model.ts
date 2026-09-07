import { Paciente, Psicologo } from './clinica.model';

export interface Cita {
  id: string;
  paciente: string | Paciente;
  psicologo: string | Psicologo;
  paciente_nombre?: string;
  psicologo_nombre?: string;
  paciente_expediente?: string;
  fecha: string; // YYYY-MM-DD
  hora_inicio: string; // HH:MM:SS
  hora_fin: string; // HH:MM:SS
  modalidad: 'PRESENCIAL' | 'VIRTUAL';
  estado: 'PROGRAMADA' | 'CONFIRMADA' | 'REALIZADA' | 'CANCELADA' | 'INASISTENCIA';
  motivo_consulta?: string;
  costo: number;
  fecha_creacion?: string;
  teleconsulta_id?: string;
}

export interface SlotDisponible {
  hora_inicio: string;
  hora_fin: string;
  disponible: boolean;
}

export interface TeleconsultaAccess {
  cita_id: string;
  room_name: string;
  domain: string;
  jwt_token?: string;
  display_name: string;
  email: string;
  is_moderator: boolean;
}

export interface AlertaClinica {
  id: string;
  paciente: string;
  paciente_nombre?: string;
  codigo_expediente?: string;
  tipo: 'INASISTENCIA_REITERADA' | 'RIESGO_DESERCION' | 'URGENCIA_CLINICA';
  severidad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
  descripcion: string;
  resuelta: boolean;
  fecha_creacion: string;
  fecha_resolucion?: string;
}

export interface DashboardKPIs {
  periodo: string;
  citas_hoy: number;
  total_citas_mes: number;
  tasa_ausentismo_pct: number;
  distribucion_estados: {
    PROGRAMADA: number;
    CONFIRMADA: number;
    REALIZADA: number;
    CANCELADA: number;
    INASISTENCIA: number;
  };
  ocupacion_por_psicologo: Array<{
    psicologo_id: string;
    nombre: string;
    total_citas: number;
    horas_atendidas: number;
  }>;
  alertas_activas: AlertaClinica[];
}
