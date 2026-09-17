import { Paciente, Psicologo } from './clinica.model';
import { Cita } from './agenda.model';

export interface FormularioPreConsulta {
  id: string;
  titulo: string;
  descripcion?: string;
  preguntas_json: Array<{
    id: string;
    texto: string;
    tipo: 'texto' | 'opcion_multiple' | 'escala_1_5' | 'booleano';
    opciones?: string[];
    requerido: boolean;
  }>;
  version: number;
  activo: boolean;
  fecha_creacion: string;
}

export interface RespuestaPreConsulta {
  id: string;
  formulario: string | FormularioPreConsulta;
  formulario_titulo?: string;
  cita: string | Cita;
  paciente: string | Paciente;
  paciente_nombre?: string;
  psicologo_nombre?: string;
  respuestas_json: Record<string, any>;
  completado: boolean;
  fecha_respuesta?: string;
  consentimiento_ia_procesamiento: boolean;
  analisis_ia_previo?: any;
}

export interface DiagnosticoCIE {
  id: string;
  codigo_cie10: string;
  descripcion: string;
  tipo: 'PRINCIPAL' | 'SECUNDARIO' | 'PRESUNTIVO' | 'DESCARTADO';
  fecha_diagnostico: string;
  notas_criterio?: string;
}

export interface HistoriaClinica {
  id: string;
  paciente: string | Paciente;
  paciente_nombre?: string;
  psicologo_cabecera: string | Psicologo;
  psicologo_nombre?: string;
  numero_historia: string;
  fecha_apertura: string;
  motivo_consulta_inicial?: string;
  anamnesis?: string;
  antecedentes_personales?: string;
  antecedentes_familiares?: string;
  examen_estado_mental?: string;
  plan_terapeutico?: string;
  objetivos_terapeuticos?: string[];
  activo: boolean;
  diagnosticos: DiagnosticoCIE[];
  total_sesiones?: number;
  total_tareas?: number;
  alertas_recaida?: number;
  ultima_sesion?: string;
}

export interface NotaSesion {
  id: string;
  historia_clinica: string;
  cita?: string | Cita;
  psicologo: string | Psicologo;
  psicologo_nombre?: string;
  numero_sesion: number;
  fecha_sesion: string;
  subjetivo: string;
  objetivo: string;
  analisis: string;
  plan: string;
  intervenciones_aplicadas?: string;
  nivel_riesgo: 'BAJO' | 'MODERADO' | 'ALTO' | 'CRITICO';
  firmado: boolean;
  fecha_firma?: string;
  firma_hash_integridad?: string;
  es_borrador: boolean;
  ultima_actualizacion_borrador?: string;
  duracion_minutos?: number;
}

export interface EvolucionClinica {
  id: string;
  historia_clinica: string;
  nota_sesion?: string;
  fecha_registro: string;
  puntuacion_escala?: number;
  indicador_progreso: 'RETROCESO' | 'ESTABLE' | 'LEVE_MEJORIA' | 'MEJORIA_SIGNIFICATIVA' | 'OBJETIVO_ALCANZADO';
  alerta_crisis_recaida: boolean;
  descripcion_crisis?: string;
  recomendacion_inmediata?: string;
}

export interface EvidenciaTarea {
  id: string;
  tarea: string;
  fecha_registro: string;
  reflexion_paciente: string;
  nivel_dificultad_percibido: number;
  archivo_adjunto?: string;
}

export interface TareaTerapeutica {
  id: string;
  historia_clinica: string;
  cita_origen?: string;
  titulo: string;
  instrucciones: string;
  categoria: 'REGISTRO_PENSAMIENTOS' | 'CONDUCTUAL' | 'MINDFULNESS' | 'LECTURA' | 'OTRO';
  fecha_asignacion: string;
  fecha_limite: string;
  estado: 'PENDIENTE' | 'COMPLETADA' | 'REVISADA' | 'VENCIDA';
  feedback_psicologo?: string;
  evidencias: EvidenciaTarea[];
}

export interface ConsentimientoInformado {
  id: string;
  codigo_plantilla: string;
  titulo: string;
  cuerpo_plantilla: string;
  version: number;
  activo: boolean;
  fecha_creacion: string;
}

export interface FirmaConsentimiento {
  id: string;
  plantilla: string | ConsentimientoInformado;
  plantilla_titulo?: string;
  paciente: string | Paciente;
  paciente_nombre?: string;
  fecha_firma: string;
  contenido_final_renderizado: string;
  ip_origen: string;
  user_agent?: string;
  hash_integridad: string;
  firma_imagen?: string;
  revocado: boolean;
  motivo_revocacion?: string;
}

export interface DerivacionCaso {
  id: string;
  historia_clinica: string;
  paciente_nombre?: string;
  psicologo_derivante: string;
  psicologo_nombre?: string;
  tipo_cierre: 'ALTA_TERAPEUTICA' | 'DERIVACION_PSIQUIATRIA' | 'DERIVACION_MEDICA' | 'ABANDONO' | 'ADMINISTRATIVO';
  especialidad_destino?: string;
  profesional_o_institucion_destino?: string;
  motivo_derivacion: string;
  resumen_evolucion: string;
  recomendaciones_tratamiento?: string;
  bloquear_citas_subsecuentes: boolean;
  fecha_registro: string;
  documento_orden_pdf?: string;
}

export interface CieItem {
  codigo: string;
  descripcion: string;
  categoria: string;
  subgrupo: string;
}

export interface AnalisisIARequest {
  respuestas: Record<string, any>;
  motivo_consulta?: string;
  consentimiento_paciente: boolean;
}

export interface ReglaDisparada {
  regla: string;
  evidencia: string;
  severidad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
  prioridad: number;
}

export interface AnalisisIAResponse {
  analisis_id?: string;
  puntuacion_severidad: number;
  nivel_alerta: 'NORMAL' | 'MODERADA' | 'ALTA' | 'CRITICA';
  reglas_disparadas: ReglaDisparada[];
  resumen_clinico_sugerido: string;
  preguntas_profundizacion_sugeridas: string[];
  disclaimer: string;
  sha256_verificacion: string;
}

export interface DecisionIARequest {
  analisis_id?: string;
  respuesta_preconsulta_id?: string;
  decision: 'ACEPTADO' | 'EDITADO' | 'DESCARTADO';
  texto_final_utilizado?: string;
  motivo_descarte?: string;
}
