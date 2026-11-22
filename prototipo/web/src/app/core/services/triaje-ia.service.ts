// ==============================================================================
// MÓDULO: triaje-ia.service.ts
// CAPA BCE: CONTROL (Client Service) — cliente de CTR_ClasificacionIAController y CTR_MatchingController
// CASOS DE USO: CU21 (Clasificación Asistida por IA), CU22 (Matching de Psicólogos HITL)
// HISTORIAS DE USUARIO: HU-47, HU-48
//   CU21-paso 2:  POST /ia/clasificar-triaje/
//   CU22-paso 2:  GET  /matching/sugerencias/?paciente_id=
//   CU22-paso 21: POST /matching/{id}/aprobar/
//   CU22-paso 31: POST /matching/{id}/rechazar_y_reasignar/
// ==============================================================================
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export type CategoriaTriaje =
  'ANSIEDAD_FOBIAS' | 'DEPRESION_ANIMO' | 'PAREJA_FAMILIA' | 'INFANTO_JUVENIL' | 'DUELO_ADAPTACION' | 'OTRO';
export type SeveridadTriaje = 'BAJA' | 'MODERADA' | 'ALTA' | 'CRITICA';

export interface ClasificacionIA {
  id: string;
  respuestapreconsulta: string;
  paciente_id: string;
  paciente_nombre: string;
  paciente_expediente: string;
  psicologo_asignado_nombre: string | null;
  categoria_principal: CategoriaTriaje;
  categoria_display: string;
  confianza_score: number;          // 0..1
  nivel_severidad: SeveridadTriaje;
  puntaje_severidad: number;        // 1..5
  score_severidad: number;          // 0..1 (protocolo crisis >= 0.70)
  nivel_atencion: 'CRITICO' | 'REGULAR';
  alerta_crisis: boolean;
  modelo_ia: string;
  palabras_clave_detectadas: string[];
  explicacion_heuristica: string;
  hash_trazabilidad_sha256: string;
  fecha_analisis: string;
}

export interface DatosPaciente {
  paciente_id: string;
  nombre: string;
  apellido: string;
  expediente: string;
  modalidad_preferencia: 'PRESENCIAL' | 'VIRTUAL' | 'MIXTA';
  psicologo_asignado_id: string | null;
}

/** CU21-paso 17 (crisis) / CU21-paso 25 (ordinaria): respuesta HTTP 200 OK */
export interface ClasificarTriajeResponse {
  alerta_crisis: boolean;
  nivel: 'ALTO' | 'REGULAR';
  sugerencia_inmediata?: string;
  clasificacion: ClasificacionIA;
  paciente: DatosPaciente;
}

export interface FactoresMatching {
  afinidad: number;         // 0..1
  disponibilidad: number;   // 0..1
  balance_carga: number;    // 0..1
  modalidad: number;        // 0..1
}

export interface CandidatoMatching {
  sugerencia_id: string;
  ranking: number;
  psicologo_id: string;
  nombre_psicologo: string;
  numero_colegiado: string;
  especialidades: string[];
  modalidad: string;
  score: number;            // 0..100
  factores: FactoresMatching;
  pesos: FactoresMatching;
  carga_actual: number;
  cupo_maximo: number;
  cupo_completo: boolean;
}

/** CU22-paso 18: HTTP 200 OK {top3_candidatos, scores} */
export interface SugerenciasResponse {
  paciente: DatosPaciente;
  triaje: { clasificacion_id: string; categoria: CategoriaTriaje; severidad: SeveridadTriaje; alerta_crisis: boolean };
  formula: string;
  top3_candidatos: CandidatoMatching[];
}

/** CU22-paso 28 (aprobación) / CU22-paso 38 (asignación manual): HTTP 200 OK */
export interface DecisionAsignacionResponse {
  mensaje: string;
  sugerencia_id: string;
  estado_decision: 'APROBADO' | 'RECHAZADO_MANUAL';
  paciente_id: string;
  psicologo_id: string;
  psicologo_asignado: string;
  carga_actual: number;
  cupo_maximo: number;
  asignacion_manual: boolean;
}

export const CATEGORIA_LABEL: Record<CategoriaTriaje, string> = {
  ANSIEDAD_FOBIAS: 'Ansiedad y Fobias',
  DEPRESION_ANIMO: 'Depresión y Estado de Ánimo',
  PAREJA_FAMILIA: 'Pareja y Familia',
  INFANTO_JUVENIL: 'Infanto-Juvenil',
  DUELO_ADAPTACION: 'Duelo y Adaptación',
  OTRO: 'Otro motivo clínico',
};

/** Extrae el mensaje {"error": "..."} que devuelve el backend, con un texto por defecto según el status. */
export function mensajeErrorApi(err: HttpErrorResponse, porDefecto: string): string {
  const e = err?.error;
  if (e && typeof e === 'object') {
    if (typeof e.error === 'string') return e.error;
    if (typeof e.detail === 'string') return e.detail;
  }
  if (err?.status === 0) return 'No se pudo conectar con el servidor.';
  if (err?.status === 403) return 'No tiene permisos para operar el triaje IA (solo Coordinador Clínico / Administrador).';
  return porDefecto;
}

@Injectable({ providedIn: 'root' })
export class TriajeIAService {
  private apiUrl = `${environment.apiUrl}/clinica`;

  constructor(private http: HttpClient) {}

  /** HU-47 (c): alertas de crisis para la consola del coordinador. */
  getAlertasCrisis(): Observable<ClasificacionIA[]> {
    return this.http.get<ClasificacionIA[]>(`${this.apiUrl}/triaje/alertas/`);
  }

  /** Clasificaciones emitidas (crisis primero, luego las más recientes). */
  getClasificaciones(): Observable<ClasificacionIA[]> {
    return this.http.get<ClasificacionIA[]>(`${this.apiUrl}/clasificacion-ia/`);
  }

  /** CU21-paso 2: POST /ia/clasificar-triaje/ (re-ejecuta la inferencia sobre un intake). */
  clasificarTriaje(respuestaId: string): Observable<ClasificarTriajeResponse> {
    return this.http.post<ClasificarTriajeResponse>(`${this.apiUrl}/ia/clasificar-triaje/`, { respuesta_id: respuestaId });
  }

  /** CU22-paso 2: GET /matching/sugerencias/?paciente_id= */
  obtenerSugerencias(pacienteId: string): Observable<SugerenciasResponse> {
    const params = new HttpParams().set('paciente_id', pacienteId);
    return this.http.get<SugerenciasResponse>(`${this.apiUrl}/matching/sugerencias/`, { params });
  }

  /** CU22-paso 21: POST /matching/{id}/aprobar/ {psicologo_id} */
  aprobar(sugerenciaId: string, psicologoId: string): Observable<DecisionAsignacionResponse> {
    return this.http.post<DecisionAsignacionResponse>(`${this.apiUrl}/matching/${sugerenciaId}/aprobar/`,
      { psicologo_id: psicologoId });
  }

  /** CU22-paso 31: POST /matching/{id}/rechazar_y_reasignar/ {psicologo_manual_id, motivo} */
  rechazarYReasignar(sugerenciaId: string, psicologoManualId: string, motivo: string): Observable<DecisionAsignacionResponse> {
    return this.http.post<DecisionAsignacionResponse>(`${this.apiUrl}/matching/${sugerenciaId}/rechazar_y_reasignar/`,
      { psicologo_manual_id: psicologoManualId, motivo });
  }
}
