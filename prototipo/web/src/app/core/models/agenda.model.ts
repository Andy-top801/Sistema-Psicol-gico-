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
  paciente?: string;
  paciente_nombre: string;
  codigo_expediente: string;
  tipo: 'INASISTENCIA_REITERADA' | 'RIESGO_DESERCION' | 'URGENCIA_CLINICA' | string;
  severidad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA' | string;
  descripcion: string;
  resuelta?: boolean;
  fecha_creacion: string;
  fecha_resolucion?: string;
  centro_nombre?: string;
}

export interface DashboardKPIs {
  periodo: {
    anio: number;
    mes: number;
    fecha_actual: string;
    modo?: string;
  } | any;
  citas_hoy?: {
    total: number;
    programadas: number;
    confirmadas: number;
    realizadas: number;
    canceladas: number;
    inasistencias: number;
  };
  citas_mes?: {
    total: number;
    programadas: number;
    confirmadas: number;
    realizadas: number;
    canceladas: number;
    inasistencias: number;
    tasa_ausentismo_pct: number;
    tasa_asistencia_pct: number;
    ingresos_mes: number;
  };
  total_citas_hoy: number;
  total_citas_mes: number;
  tasa_ausentismo_pct: number;
  tasa_asistencia_pct?: number;
  ingresos_mes?: number;
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
    colegiado?: string;
    total_citas: number;
    horas_atendidas: number;
    realizadas?: number;
    inasistencias?: number;
    ingresos_generados?: number;
  }>;
  alertas_activas: AlertaClinica[];
  alertas_pendientes?: {
    total: number;
    lista: any[];
  };
}
